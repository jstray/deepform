import argparse

import wandb

from deepform.common import MODEL_DIR, WANDB_ENTITY, WANDB_PROJECT

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="download a model stored in W&B")
    parser.add_argument(
        "-v",
        "--version",
        dest="version",
        help="model version to download",
        default="latest",
    )
    args = parser.parse_args()

    run = wandb.init(
        project="model-download",
        entity=WANDB_ENTITY,
        job_type="ps",
        allow_val_change=True,
    )
    config = run.config
    model_name = config.model_artifact_name
    artifact_name = f"{WANDB_ENTITY}/{WANDB_PROJECT}/{model_name}:{args.version}"
    artifact = run.use_artifact(artifact_name, type="model")
    artifact_alias = artifact.metadata.get("name") or "unknown"
    artifact.download(root=(MODEL_DIR / artifact_alias))
