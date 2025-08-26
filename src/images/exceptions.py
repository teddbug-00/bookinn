from starlette import status

from src.exceptions.base import AppError


class ImageUploadFailedException(AppError):
    """Raised when an image upload fails for an unspecified reason."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self):
        message = "Image upload failed. Please try again later."
        super().__init__(message)


class ThumbnailAlreadyExistsException(AppError):
    """Raised when attempting to set a thumbnail for a listing that already has one."""
    status_code = status.HTTP_409_CONFLICT

    def __init__(self):
        message = "A thumbnail for this listing already exists. Please unset the current thumbnail first."
        super().__init__(message)
