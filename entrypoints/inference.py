"""
Inference Entrypoint

This script runs the production inference pipeline using
the pre-trained LightGBM model and saves predictions.
"""

from src.pipelines.inference_pipeline import run_inference


def main():
    print("Starting inference pipeline...")

    run_inference(
        config_path="config/local.yaml"
    )

    print("Inference completed successfully.")


if __name__ == "__main__":
    main()
