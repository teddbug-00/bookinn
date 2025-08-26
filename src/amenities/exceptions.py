import uuid

from starlette import status

from src.exceptions.base import AppError


class AmenityNotFoundException(AppError):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, amenity_id: uuid.UUID):
        message = f"Amenity with ID '{amenity_id}' was not found."
        super().__init__(message)


class AmenityAlreadyExistsException(AppError):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, name: str):
        message = f"Amenity with name '{name}' already exists."
        super().__init__(message)
