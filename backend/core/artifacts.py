# backend/core/artifacts.py

import logging
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)


class ArtifactDownloadError(Exception):
    """Failed to fetch a required artifact from s3."""


_s3 = boto3.client("s3")


def download_file(bucket: str, key: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    try:
        _s3.download_file(bucket, key, str(tmp))
    except (BotoCoreError, ClientError) as e:
        tmp.unlink(missing_ok=True)
        raise ArtifactDownloadError(
            f"Failed to download s3://{bucket}/{key}: {e}"
        ) from e
    tmp.replace(dest)


def download_prefix(bucket: str, prefix: str, dest_dir: Path) -> None:
    prefix = prefix.rstrip("/") + "/"
    count = 0
    try:
        paginator = _s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.endswith("/"):
                    continue
                download_file(bucket, key, dest_dir / key[len(prefix) :])
                count += 1
    except (BotoCoreError, ClientError) as e:
        raise ArtifactDownloadError(f"Failed to list s3://{bucket}/{key}: {e}") from e
        if count == 0:
            raise ArtifactDownloadError(
                f"No objects under s3://{bucket}/{key}: {e}"
            ) from e
    logger.info("Downloaded %d files from s3://%s/%s", count, bucket, prefix)
