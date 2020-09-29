"""Use a model to infer predicted values for a document."""


import argparse

import numpy as np

from deepform.data.add_features import TokenType
from deepform.data.tokenize_pdfs import extract_doc
from deepform.model import load_model


def infer_from_pdf(pdf_path, model=None, window_len=None):
    """Extract features from a PDF and run infrence on it."""
    if not model:
        model, window_len = load_model()
    if not window_len:
        raise Exception("No window_len param provided or inferrable")

    doc = extract_doc(pdf_path, window_len)

    best_score_texts, individual_scores, _ = doc.predict_answer(model)

    # TODO: clean up the column name from the token type enum
    predictions = {
        str(column.name.lower()): {"prediction": text, "score": score}
        for text, score, column in zip(
            best_score_texts, individual_scores, np.array(TokenType)[1:]
        )
    }

    return predictions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-m", "--model", dest="model", help="model file to use in prediction"
    )
    parser.add_argument("pdf", nargs="+", help="pdf to run inference on")
    args = parser.parse_args()
    model, window_len = load_model(args.model)

    for pdf in args.pdf:
        predictions = infer_from_pdf(pdf, model, window_len)
        print(f"predictions for {pdf}")
        print(predictions)
