import boto3
import os
from pathlib import Path


def get_aws_session():
    project_root = Path(__file__).resolve().parent.parent
    credentials_path = project_root / "credentials" / "aws_credentials.cfg"

    if credentials_path.is_file():
        os.environ["AWS_SHARED_CREDENTIALS_FILE"] = str(credentials_path)

        return boto3.Session(
            profile_name="default",
            region_name="us-east-1"
        )

    # Use AWS's default credential chain when running in Lambda, etc.
    return boto3.Session(region_name="us-east-1")