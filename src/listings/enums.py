import enum


class PricingUnit(str, enum.Enum):
    """Defines the unit for the price of a listing."""
    PER_NIGHT = "per_night"
    PER_MONTH = "per_month"
    PER_YEAR = "per_year"


class ListingType(str, enum.Enum):
    """An enum for different types of listings."""
    HOTEL = "hotel"
    HOSTEL = "hostel"
    APARTMENT = "apartment"
    GUESTHOUSE = "guesthouse"
