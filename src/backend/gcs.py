import os
import tempfile

from filelock import FileLock  
from google.cloud import storage

from src.core import StorageBackend


class GCSBackend(StorageBackend):
    LOCAL_ARTIFACT_DIR = os.path.join(tempfile.gettempdir(), "model_artifact")
    LOCK_FILE = os.path.join(tempfile.gettempdir(), "model_artifact.lock")

    @classmethod
    def download_artifact(cls, uri: str) -> str:
        print(f"Starting model artifact download from URI: {uri}")

        if not uri.startswith("gs://"):
            if os.path.isdir(uri):
                return uri
            raise ValueError(f"Invalid GCS uri format: {uri}")

        parts = uri[5:].split("/", 1)
        bucket_name = parts[0]
        blob_prefix = parts[1] if len(parts) > 1 else ""

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        lock = FileLock(cls.LOCK_FILE)
        with lock:
            if os.path.exists(cls.LOCAL_ARTIFACT_DIR):
                print("model exists")
                return cls.LOCAL_ARTIFACT_DIR


            os.makedirs(cls.LOCAL_ARTIFACT_DIR, exist_ok=True)

            blobs = bucket.list_blobs(prefix=blob_prefix)
            downloaded_count = 0

            for blob in blobs:
                relative_path = os.path.relpath(blob.name, blob_prefix)
                if not relative_path.strip() or relative_path.endswith("/"):
                    continue

                local_path = os.path.join(cls.LOCAL_ARTIFACT_DIR, relative_path)

                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                blob.download_to_filename(local_path)
                downloaded_count += 1

            print(f"Successfully downloaded {downloaded_count} files to {cls.LOCAL_ARTIFACT_DIR}")
            return cls.LOCAL_ARTIFACT_DIR

    @classmethod
    def download_file(cls, uri: str) -> bytes:
        if not uri.startswith("gs://"):
            raise ValueError(f"Invalid GCS URI format: {uri}")

        parts = uri[5:].split("/", 1)
        bucket_name = parts[0]
        blob_name = parts[1]

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        try: 
            downloaded_byte = blob.download_as_bytes()
        except Exception as e:
            print(f"File not found in GCS: {uri}")

        return downloaded_byte