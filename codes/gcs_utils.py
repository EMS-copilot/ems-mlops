import os
import tempfile
from google.cloud import storage

LOCAL_ARTIFACT_DIR = os.path.join(tempfile.gettempdir(), "cpr_model_artifact")


def download_single_file_to_memory(gcs_uri: str) -> bytes:
    if not gcs_uri.startswith("gs://"):
        raise ValueError(f"Invalid GCS URI format: {gcs_uri}")

    parts = gcs_uri[5:].split("/", 1)
    bucket_name = parts[0]
    blob_name = parts[1]

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    if not blob.exists():
        raise FileNotFoundError(f"File not found in GCS: {gcs_uri}")

    return blob.download_as_bytes()


def download_all_artifacts(artifact_uri: str) -> str:
    print(f"Starting model artifact download from URI: {artifact_uri}")

    if not artifact_uri.startswith("gs://"):
        if os.path.isdir(artifact_uri):
            return artifact_uri
        raise ValueError(f"Invalid GCS artifact_uri format: {artifact_uri}")

    parts = artifact_uri[5:].split("/", 1)
    bucket_name = parts[0]
    blob_prefix = parts[1] if len(parts) > 1 else ""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    if os.path.exists(LOCAL_ARTIFACT_DIR):
        import shutil

        shutil.rmtree(LOCAL_ARTIFACT_DIR)

    os.makedirs(LOCAL_ARTIFACT_DIR, exist_ok=True)

    blobs = bucket.list_blobs(prefix=blob_prefix)
    downloaded_count = 0

    for blob in blobs:
        relative_path = os.path.relpath(blob.name, blob_prefix)
        if not relative_path.strip() or relative_path.endswith("/"):
            continue

        local_path = os.path.join(LOCAL_ARTIFACT_DIR, relative_path)

        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        blob.download_to_filename(local_path)
        downloaded_count += 1

    print(f"Successfully downloaded {downloaded_count} files to {LOCAL_ARTIFACT_DIR}")
    return LOCAL_ARTIFACT_DIR
