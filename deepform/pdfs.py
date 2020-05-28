import logging
from pathlib import Path

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError

BUCKET_NAME = "project-deepform"
LOCAL_PATH = Path().absolute().parent / "data" / "pdfs"


def get_pdf_path(slug):
    """Return a path to the pdf with the given slug, downloading the file if necessary.

    If the pdf isn't in the local file system, download it from an external repository.
    """
    filename = slug + ("" if slug.endswith(".pdf") else ".pdf")
    location = LOCAL_PATH / filename
    if not location.is_file():
        LOCAL_PATH.mkdir(parents=True, exist_ok=True)
        download_from_remote(location)
    return location


def download_from_remote(local_path):
    """Copy a pdf from S3 into the local filesystem."""
    filename = local_path.name
    s3_key = "pdfs/" + filename
    s3 = boto3.resource("s3", config=Config(signature_version=UNSIGNED))
    try:
        s3.Bucket(BUCKET_NAME).download_file(s3_key, str(local_path))
    except ClientError:
        logging.error(f"Unable to retrieve {s3_key} from s3://{BUCKET_NAME}")
        raise
