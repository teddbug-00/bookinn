from starlette import status

from src.exceptions.base import AppError


class CloudinaryUploadException(AppError):
    """Raised when an error occurs during an upload to Cloudinary."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    def __init__(self):
        message = "Failed to upload image to storage service. Please try again later."
        super().__init__(message)
