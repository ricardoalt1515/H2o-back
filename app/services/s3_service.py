import aioboto3
import os
from typing import IO, Optional

S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")

async def upload_file_to_s3(file_obj: IO[bytes], filename: str, content_type: Optional[str] = None) -> str:
    session = aioboto3.Session()
    extra_args = {"ContentType": content_type} if content_type else {}
    async with session.client(
        "s3",
        region_name=S3_REGION,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
    ) as s3:
        await s3.upload_fileobj(file_obj, S3_BUCKET, filename, ExtraArgs=extra_args)
    return filename  # La key en S3

async def get_presigned_url(filename: str, expires: int = 3600) -> str:
    session = aioboto3.Session()
    async with session.client(
        "s3",
        region_name=S3_REGION,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
    ) as s3:
        url = await s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": filename},
            ExpiresIn=expires,
        )
        return url
