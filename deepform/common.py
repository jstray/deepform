from pathlib import Path

S3_BUCKET = "project-deepform"

ROOT_DIR = Path(__file__).absolute().parents[1]
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"
PDF_DIR = DATA_DIR / "pdfs"
TOKEN_DIR = DATA_DIR / "tokenized"
LABELED_DIR = DATA_DIR / "labeled"
TRAINING_DIR = DATA_DIR / "training"
TRAINING_INDEX = TRAINING_DIR.parent / "doc_index.parquet"
MODEL_DIR = DATA_DIR / "models"

WANDB_PROJECT = "extract_total"
WANDB_ENTITY = "deepform"
