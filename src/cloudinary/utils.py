import cloudinary.api
import cloudinary.uploader
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool

from src.cloudinary.exceptions import CloudinaryUploadException


async def upload_image(file: UploadFile, folder: str, transformation: dict) -> dict:
    """
    Uploads an image file to a specified folder in Cloudinary.
    """
    try:
        # The upload function from the cloudinary library is synchronous,
        # so we run it in a thread pool to avoid blocking the asyncio event loop.
        result = await run_in_threadpool(
            cloudinary.uploader.upload,
            file.file,
            folder=folder,
            transformation=transformation
        )
        return result
    except Exception as e:
        raise CloudinaryUploadException() from e


async def delete_image(public_id: str) -> dict:
    """"
    Deletes a single image from Cloudinary using its public_id.
    This uses the 'destroy' method from the Upload API, which is standard for single deletions.
    """
    try:
        return await run_in_threadpool(cloudinary.uploader.destroy, public_id)
    except Exception as e:
        raise CloudinaryUploadException() from e


async def delete_folder(folder_path: str):
    """
    Deletes an entire folder and all its contents from Cloudinary using the Admin API.
    This is a two-step process for robustness: first delete all resources, then the folder.
    """
    try:
        # First, delete all resources within the folder
        await run_in_threadpool(cloudinary.api.delete_resources_by_prefix, folder_path)
        # Then, delete the now-empty folder
        await run_in_threadpool(cloudinary.api.delete_folder, folder_path)
    except Exception as e:
        raise CloudinaryUploadException() from e
