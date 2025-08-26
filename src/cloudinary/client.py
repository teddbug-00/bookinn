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

        # Define the standard transformations to be applied to all uploads
        self.transformation_rules = {
            "width": 1280,
            "height": 1280,
            "crop": "limit",
            "quality": "auto:good",
            "fetch_format": "webp"
        }
