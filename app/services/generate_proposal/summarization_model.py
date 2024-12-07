import yaml
import os
import boto3
from botocore.exceptions import NoCredentialsError


config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

# Load configuration
with open(config_path, "r") as f:
    config = yaml.safe_load(f)


class SummarizationModel:
    def __init__(self, model_name=config["model"]["model_path"], config=config):
        self.config = config
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.input = ""
        self.output = ""

    def generate_summary(self, max_length=1024):
        inputs = self.tokenizer(
            self.input,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=max_length,
        )

        # Generate summary (use `generate` method)
        summary_ids = self.model.generate(
            inputs["input_ids"], max_length=150, num_beams=4, early_stopping=True
        )

        # Decode the generated summary ids to text
        self.output = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    def download_from_s3(self, bucket_name, model_key):
        # Create an S3 client
        s3_client = boto3.client("s3")

        # Download the model files recursively from S3
        def download_directory_from_s3(s3_bucket, s3_prefix, local_path):
            if not os.path.exists(local_path):
                os.makedirs(local_path)

            # List objects under the specified S3 prefix (model_key)
            try:
                response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)
                if "Contents" in response:
                    for obj in response["Contents"]:
                        s3_file_key = obj["Key"]
                        local_file_path = os.path.join(
                            local_path, os.path.relpath(s3_file_key, s3_prefix)
                        )

                        # Create directories if they do not exist
                        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                        # Download the file from S3
                        print(f"Downloading {s3_file_key} to {local_file_path}")
                        s3_client.download_file(s3_bucket, s3_file_key, local_file_path)
                else:
                    print(f"No files found for {s3_prefix} in bucket {s3_bucket}")
            except NoCredentialsError:
                print("Credentials not available")
            except Exception as e:
                print(f"Error downloading from S3: {str(e)}")

        # Download the model and tokenizer from the S3 bucket to the local model_key directory
        download_directory_from_s3(
            bucket_name, model_key, config["model"]["model_path"]
        )
