import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.bookings.exceptions import NotEnoughRoomsException
from src.bookings.guesthouse import repository as booking_repository
from src.bookings.guesthouse.schemas import GuesthouseBookingCreate
from src.bookings.models import Availability
from src.listings.models import Guesthouse
from src.users.models import User


async def create_guesthouse_booking(
        db: AsyncSession, booking_in: GuesthouseBookingCreate, guesthouse: Guesthouse, user: User
):
    """
    Handles the business logic for creating a guesthouse booking, including
    availability checks and updates.
    """
    # 1. Check for availability
    num_nights = (booking_in.check_out_date - booking_in.check_in_date).days
    availability_records = await booking_repository.get_availability_for_date_range(
        db, guesthouse.id, booking_in.check_in_date, booking_in.check_out_date
    )

    availability_map = {record.date: record.available_units for record in availability_records}

    current_date = booking_in.check_in_date
    while current_date < booking_in.check_out_date:
        available_rooms = availability_map.get(current_date, guesthouse.number_of_rooms)
        if available_rooms < booking_in.number_of_rooms:
            raise NotEnoughRoomsException(date=current_date, available=available_rooms)
        current_date += datetime.timedelta(days=1)

    # 2. Calculate total price
    total_price = guesthouse.price * booking_in.number_of_rooms * num_nights

    # 3. Create the booking record
    db_booking = await booking_repository.create(db, booking_in, user.id, total_price)

    # 4. Update availability records
    current_date = booking_in.check_in_date
    while current_date < booking_in.check_out_date:
        record_to_update = next((r for r in availability_records if r.date == current_date), None)
        if record_to_update:
            record_to_update.available_units -= booking_in.number_of_rooms
        else:
            record_to_update = Availability(
                listing_id=guesthouse.id, date=current_date,
                available_units=guesthouse.number_of_rooms - booking_in.number_of_rooms
            )
        db.add(record_to_update)
        current_date += datetime.timedelta(days=1)

    await db.commit()
    await db.refresh(db_booking)
    return db_booking
