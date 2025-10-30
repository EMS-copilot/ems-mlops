from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Abstract base class for storage backends.

    A storage backend defines how model artifacts and static resources
    are retrieved, either from local file systems, cloud storage services,
    or other external sources.
    """

    @classmethod
    @abstractmethod
    def download_artifact(cls, uri: str) -> str:
        """Download all artifacts from a given URI.

        This method is intended for retrieving complete model bundles,
        such as a TensorFlow SavedModel directory, and storing them
        locally for further use.

        Args:
            uri (str): The source URI of the artifact bundle.

        Returns:
            str: Local filesystem path where the bundle has been downloaded.
        """
        pass

    @classmethod
    @abstractmethod
    def download_file(cls, uri: str) -> bytes:
        """Download a single file into memory.

        This method is intended for lightweight resources such as JSON
        or CSV files that can be consumed directly from memory.

        Args:
            uri (str): The source URI of the file.

        Returns:
            bytes: Raw file content as bytes.
        """
        pass
