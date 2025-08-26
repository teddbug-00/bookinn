import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool

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

    async def upload_image(self, file: UploadFile, folder: str) -> dict:
        """
        Uploads an image file to a specified folder in Cloudinary.
        """
        # The upload function from the cloudinary library is synchronous,
        # so we run it in a thread pool to avoid blocking the asyncio event loop.
        result = await run_in_threadpool(cloudinary.uploader.upload, file.file, folder=folder)
        return result
