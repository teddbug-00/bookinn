import uuid

from starlette import status

from src.exceptions.base import AppError


class CannotReviewOwnListingException(AppError):
    """Raised when a user attempts to review their own listing."""
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self):
        message = "You cannot review your own listing."
        super().__init__(message)


class UserAlreadyReviewedListingException(AppError):
    """Raised when a user attempts to review the same listing more than once."""
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, listing_id: uuid.UUID, reviewer_id: uuid.UUID):
        message = f"User '{reviewer_id}' has already reviewed listing '{listing_id}'."
        super().__init__(message)
