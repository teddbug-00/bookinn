import uuid

from starlette import status

from src.exceptions.base import AppError


class ListingNotFoundException(AppError):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, listing_id: uuid.UUID):
        message = f"Listing with ID '{listing_id}' was not found."
        super().__init__(message)


class InvalidAmenitiesException(AppError):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, invalid_ids: list[str]):
        message = f"The following amenity IDs are invalid or not found: {invalid_ids}"
        super().__init__(message)


class NotListingOwnerException(AppError):
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self):
        message = "You do not have permission to modify this listing."
        super().__init__(message)
