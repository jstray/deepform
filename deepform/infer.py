"""Use a model to infer predicted values for a document."""


import argparse

from deepform.data.tokenize_pdfs import extract_doc
from deepform.model import load_model, predict_answer


def infer_from_pdf(pdf_path, model_file=None):
    """Extract features from a PDF and run infrence on it."""
    model, window_len = load_model(model_file)
    doc = extract_doc(pdf_path, window_len)
    token, score, _ = predict_answer(model, doc)
    return token, score


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-m", "--model", dest="model", help="model file to use in prediction",
    )
    parser.add_argument(
        "pdf", nargs="+", help="pdf to run inference on",
    )
    args = parser.parse_args()

    model, window_len = load_model(args.model)

    for pdf in args.pdf:
        doc = extract_doc(pdf, window_len)
        token, score, _ = predict_answer(model, doc)
        print(f"Predicted '{token}' with score {score} on {pdf}")
