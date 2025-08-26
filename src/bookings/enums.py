from enum import Enum


class BookingStatus(str, Enum):
    """Defines the status of a booking."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"
