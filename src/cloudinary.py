import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool

from src.config import settings

# Configure the Cloudinary SDK with credentials from settings
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


async def upload_image(file: UploadFile, folder: str) -> dict:
    """
    Uploads an image file to a specified folder in Cloudinary.

    :param file: The image file to upload, as an UploadFile object.
    :param folder: The name of the folder in Cloudinary to store the image.
    :return: A dictionary containing the upload result from Cloudinary.
    """
    # The upload function from the cloudinary library is synchronous,
    # so we run it in a thread pool to avoid blocking the asyncio event loop.
    result = await run_in_threadpool(cloudinary.uploader.upload, file.file, folder=folder)
    return result