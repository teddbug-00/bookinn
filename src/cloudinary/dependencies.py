from functools import lru_cache

from src.cloudinary.client import CloudinaryClient


@lru_cache
def get_cloudinary_client() -> CloudinaryClient:
    """
    Provides a singleton instance of the CloudinaryClient.
    Using lru_cache ensures the client is instantiated only once.
    """
    return CloudinaryClient()
