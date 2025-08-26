import cloudinary.uploader
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool

from src.cloudinary.exceptions import CloudinaryUploadException


async def upload_image(file: UploadFile, folder: str) -> dict:
    """
    Uploads an image file to a specified folder in Cloudinary.
    """
    try:
        # The upload function from the cloudinary library is synchronous,
        # so we run it in a thread pool to avoid blocking the asyncio event loop.

        # Define transformations to be applied on upload
        transformation = {
            "width": 1280,  # Max width
            "height": 1280,  # Max height
            "crop": "limit",  # Resize without cropping, maintaining aspect ratio
            "quality": "auto:good",  # Automatically adjust quality to a good level
            "fetch_format": "webp"  # Convert to the modern, efficient WebP format
        }

        result = await run_in_threadpool(
            cloudinary.uploader.upload,
            file.file,
            folder=folder,
            transformation=transformation
        )
        return result
    except Exception as e:
        raise CloudinaryUploadException() from e
