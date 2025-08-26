from enum import Enum


class BookingStatus(str, Enum):
    """Defines the status of a booking."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"


class BookingType(str, Enum):
    """An enum for different types of bookings, mirroring ListingType."""
    APARTMENT = "apartment"
    GUESTHOUSE = "guesthouse"
    HOSTEL = "hostel"
    HOTEL = "hotel"
