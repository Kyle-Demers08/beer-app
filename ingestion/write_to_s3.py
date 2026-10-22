
import argparse
from pathlib import Path
from utils.aws_connection import get_aws_session


def upload_to_s3(restaurant_id):
    session = get_aws_session()
    s3 = session.client("s3")

    bucket_name = "beer-persona-data-dev"

    # Build paths using restaurant_id
    project_root = Path(__file__).resolve().parent.parent

    local_file = (
        project_root / "data" / "raw" / restaurant_id / "menu_items.json"
    )

    s3_key = f"raw/{restaurant_id}/menu_items.json"

    if not local_file.is_file():
        raise FileNotFoundError(f"File not found: {local_file}")

    s3.upload_file(
        Filename=str(local_file),
        Bucket=bucket_name,
        Key=s3_key
    )

    print(f"Successfully uploaded to s3://{bucket_name}/{s3_key}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload a restaurant's menu JSON to S3"
    )

    parser.add_argument(
        "restaurant_id",
        help="Restaurant folder name, e.g. bronson_bier_hall"
    )

    args = parser.parse_args()

    upload_to_s3(args.restaurant_id)
