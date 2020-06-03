import logging
from concurrent.futures import ThreadPoolExecutor

import boto3
import numpy as np
import pdfplumber
import wandb
from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError
from tqdm import tqdm

from deepform.common import PDF_DIR, S3_BUCKET
from deepform.util import docrow_to_bbox, dollar_match


def get_pdf_path(slug):
    """Return a path to the pdf with the given slug, downloading the file if necessary.

    If the pdf isn't in the local file system, download it from an external repository.
    """
    filename = slug + ("" if slug.endswith(".pdf") else ".pdf")
    location = PDF_DIR / filename
    if not location.is_file():
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        download_from_remote(location)
    return location


def get_pdf_paths(slugs):
    with ThreadPoolExecutor() as executor:
        print(f"Getting {len(slugs):,} pdfs...")
        for path in tqdm(executor.map(get_pdf_path, slugs), total=len(slugs)):
            yield path


def download_from_remote(local_path):
    """Copy a pdf from S3 into the local filesystem."""
    filename = local_path.name
    s3_key = "pdfs/" + filename
    s3 = boto3.resource("s3", config=Config(signature_version=UNSIGNED))
    try:
        s3.Bucket(S3_BUCKET).download_file(s3_key, str(local_path))
    except ClientError:
        logging.error(f"Unable to retrieve {s3_key} from s3://{S3_BUCKET}")
        raise


def log_pdf(doc, score, scores, predict_text, answer_text):
    fname = get_pdf_path(doc.slug)
    try:
        pdf = pdfplumber.open(fname)
    except Exception:
        # If the file's not there, that's fine -- we use available PDFs to
        # define what to see
        print(f"Cannot open pdf {fname}")
        return

    print(f"Rendering output for {fname}")

    # Get the correct answers: find the indices of the token(s) labelled 1
    target_idx = [idx for (idx, val) in enumerate(doc.labels) if val == 1]

    # Draw the machine output: get a score for each token
    page_images = []
    for pagenum, page in enumerate(pdf.pages):
        im = page.to_image(resolution=300)

        # training data has 0..1 for page range (see create-training-data.py)
        num_pages = len(pdf.pages)
        if num_pages > 1:
            current_page = pagenum / float(num_pages - 1)
        else:
            current_page = 0.0

        # Draw guesses
        rel_score = scores / score
        page_match = np.isclose(doc.tokens["page"], current_page)
        for token in doc.tokens[page_match & (rel_score > 0.5)].itertuples():
            if rel_score[token.Index] == 1:
                w = 5
                s = "magenta"
            elif rel_score[token.Index] >= 0.75:
                w = 3
                s = "red"
            else:
                w = 1
                s = "red"
            im.draw_rect(docrow_to_bbox(token), stroke=s, stroke_width=w, fill=None)

        # Draw target tokens
        target_toks = [
            doc.tokens.iloc[i]
            for i in target_idx
            if np.isclose(doc.tokens.iloc[i]["page"], current_page)
        ]
        rects = [docrow_to_bbox(t) for t in target_toks]
        im.draw_rects(rects, stroke="blue", stroke_width=3, fill=None)

        page_images.append(wandb.Image(im.annotated, caption="page " + str(pagenum)))

    # get best matching score of any token in the training data
    match = doc.tokens["match"].max()
    caption = (
        f"{doc.slug} guessed:{predict_text} answer:{answer_text} match:{match:.2f}"
    )
    if dollar_match(predict_text, answer_text):
        caption = "CORRECT " + caption
    else:
        caption = "INCORRECT " + caption
    wandb.log({caption: page_images})
