from fastapi import APIRouter

from src.amenities.router import router as amenities_router
from src.auth.router import router as auth_router
from src.listings.router import router as listings_router
from src.users.router import router as users_router

# This is the master router that will include all the feature-specific routers.
# It provides a single entry point for the AppFactory to include all API routes.
# This makes it easy to add a global prefix (like /api/v1) to all routes in one place.
api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(amenities_router)
api_router.include_router(listings_router)
