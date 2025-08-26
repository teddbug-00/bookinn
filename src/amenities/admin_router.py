import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.amenities import services
from src.amenities.schemas import AmenityCreate, AmenityRead, AmenityUpdate
from src.auth.dependencies import get_current_admin_user
from src.database import get_db_session

router = APIRouter(
    prefix="/amenities",
    dependencies=[Depends(get_current_admin_user)]
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AmenityRead)
async def create_new_amenity(
        amenity_in: AmenityCreate,
        session: AsyncSession = Depends(get_db_session),
):
    """Create a new amenity (Admins only)."""
    return await services.create_amenity(session, amenity_in)


@router.patch("/{amenity_id}", response_model=AmenityRead)
async def update_existing_amenity(
        amenity_id: uuid.UUID,
        amenity_in: AmenityUpdate,
        session: AsyncSession = Depends(get_db_session),
):
    """Update an amenity's information (Admins only)."""
    amenity = await services.get_amenity_by_id(session, amenity_id)
    return await services.update_amenity(session, amenity, amenity_in)


@router.delete("/{amenity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_amenity(
        amenity_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session),
):
    """Delete an amenity (Admins only)."""
    await services.delete_amenity(session, amenity_id)
    return None
