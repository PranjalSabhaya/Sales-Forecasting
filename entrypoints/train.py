"""
Training Entrypoint (Offline / Reproducibility)

IMPORTANT
---------
- This script retrains the model using pre-generated features.
- Feature engineering must be executed BEFORE running this.
- Production system does NOT call this.
- Retraining requires overwrite=True.
"""

from src.pipelines.training_pipeline import train_model


def main():
    print("Starting OFFLINE training pipeline...")
    print(" This is intended for reproducibility, not daily execution.")

    try:
        model, metrics = train_model(
            overwrite=True   # Set False to prevent overwriting
        )

        print("✅ Training completed successfully.")
        print("📊 Metrics:", metrics)

    except FileNotFoundError as e:
        print("Feature file not found.")
        print("Run feature engineering before training.")
        print(e)

    except RuntimeError as e:
        print("Training aborted.")
        print(e)

    except Exception as e:
        print("Unexpected error occurred.")
        print(e)


if __name__ == "__main__":
    main()
