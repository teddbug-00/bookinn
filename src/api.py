from fastapi import APIRouter

from src.amenities.admin_router import router as amenities_admin_router
from src.amenities.router import router as public_amenities_router
from src.auth.router import router as auth_router
from src.bookings.router import router as bookings_router
from src.images.router import router as images_router
from src.listings.router import router as listings_router
from src.reviews.router import router as reviews_router
from src.users.router import router as users_router

# This is the master router for all public-facing API routes.
api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(listings_router)
api_router.include_router(reviews_router)
api_router.include_router(images_router)
api_router.include_router(public_amenities_router)
api_router.include_router(bookings_router)

# This is the master router for all admin-only API routes.
admin_api_router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

admin_api_router.include_router(amenities_admin_router)
