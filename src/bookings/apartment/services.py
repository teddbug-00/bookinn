from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.bookings import repository as generic_booking_repo
from src.bookings.apartment import repository as apartment_booking_repo
from src.bookings.apartment.schemas import ApartmentBookingCreate
from src.bookings.exceptions import ListingNotAvailableException, InvalidLeasePeriodException
from src.listings.models import Apartment
from src.users.models import User


async def create_apartment_booking(db: AsyncSession, booking_in: ApartmentBookingCreate, apartment: Apartment,
                                   user: User):
    """
    Handles the business logic for creating a booking for an apartment.
    """
    # 1. Business Rule: Check for minimum lease period
    if booking_in.number_of_months < apartment.min_lease_months:
        raise InvalidLeasePeriodException(min_months=apartment.min_lease_months)

    # 2. Calculate check-out date and check for availability
    check_out_date = booking_in.check_in_date + relativedelta(months=booking_in.number_of_months)
    is_unavailable = await generic_booking_repo.check_for_overlapping_bookings(
        db, apartment.id, booking_in.check_in_date, check_out_date
    )
    if is_unavailable:
        raise ListingNotAvailableException()

    # 3. Calculate total price
    total_price = apartment.price * booking_in.number_of_months

    # 4. Create the booking record
    db_booking = await apartment_booking_repo.create(db, booking_in, user.id, total_price, check_out_date)
    await db.commit()
    await db.refresh(db_booking)

    return db_booking
