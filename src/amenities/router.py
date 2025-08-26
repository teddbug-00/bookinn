from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.amenities import services
from src.amenities.schemas import AmenityRead
from src.database import get_db_session

router = APIRouter(prefix="/amenities", tags=["Amenities"])


@router.get("/", response_model=Sequence[AmenityRead])
async def get_all_amenities(session: AsyncSession = Depends(get_db_session)):
    """Get all available amenities."""
    return await services.get_amenities(session)
