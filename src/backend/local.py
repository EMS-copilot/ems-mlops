import os
import shutil
import tempfile

from src.core import StorageBackend


class LocalBackend(StorageBackend):
    LOCAL_ARTIFACT_DIR = os.path.join(tempfile.gettempdir(), "model_artifact")

    @classmethod
    def download_artifact(cls, uri: str) -> str:
        if not os.path.isdir(uri):
            raise ValueError(f"Invalid local artifact directory: {uri}")

        if os.path.exists(cls.LOCAL_ARTIFACT_DIR):
            shutil.rmtree(cls.LOCAL_ARTIFACT_DIR)

        shutil.copytree(uri, cls.LOCAL_ARTIFACT_DIR)

        print(f"Successfully copied artifacts from {uri} to {cls.LOCAL_ARTIFACT_DIR}")
        return cls.LOCAL_ARTIFACT_DIR

    @classmethod
    def download_file(cls, uri: str) -> bytes:
        if not os.path.isfile(uri):
            raise FileNotFoundError(f"File not found: {uri}")

        with open(uri, "rb") as f:
            return f.read()
