import sys

from src.pipelines.inference_pipeline import run_inference


def main():
    print("🚀 Starting inference pipeline...")

    try:
        run_inference(
            config_path="config/local.yaml"
        )

        print("✅ Inference completed successfully.")

    except FileNotFoundError as e:
        print("❌ Required file not found.")
        print(e)
        sys.exit(1)

    except ValueError as e:
        print("❌ Data validation failed.")
        print(e)
        sys.exit(1)

    except Exception as e:
        print("❌ Unexpected error occurred.")
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
