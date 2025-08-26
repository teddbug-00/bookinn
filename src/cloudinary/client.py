import cloudinary

from src.cloudinary.config import cloudinary_settings


class CloudinaryClient:
    """A client for interacting with the Cloudinary API."""

    def __init__(self):
        # Configure the Cloudinary SDK upon client instantiation
        cloudinary.config(
            cloud_name=cloudinary_settings.CLOUDINARY_CLOUD_NAME,
            api_key=cloudinary_settings.CLOUDINARY_API_KEY,
            api_secret=cloudinary_settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
