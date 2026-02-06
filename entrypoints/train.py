"""
Training Entrypoint (Offline / Reproducibility)

IMPORTANT:

- This script is for OFFLINE retraining only.
- The production system uses the pre-trained model.
- Retraining will FAIL unless overwrite=True is explicitly set.
"""

from src.pipelines.training_pipeline import train_model


def main():
    print("Starting OFFLINE training pipeline....")
    print("This is intended for reproducibility, not daily execution")

    try:
        model, metrics = train_model(
            raw_data_dir="data/raw",
            overwrite=False   # change to True ONLY if you want retraining
        )

        print("Training completed successfully")
        print("Metrics:", metrics)

    except RuntimeError as e:
        print("❌ Training aborted:")
        print(e)


if __name__ == "__main__":
    main()
