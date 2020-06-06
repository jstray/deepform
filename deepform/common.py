from pathlib import Path

S3_BUCKET = "project-deepform"

ROOT_DIR = Path(__file__).absolute().parents[1]
DATA_DIR = ROOT_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
TOKEN_DIR = DATA_DIR / "tokenized"
MODEL_DIR = DATA_DIR / "models"
