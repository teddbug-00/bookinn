from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import App
from src.database import get_db_session

app = (
    App().title("BookInn API")
    .description("API for the BookInn service, providing functionalities for property listings and bookings.")
    .version("0.1.0")
    .routers()
    .exception_handlers()
    .create()
)


# --- Monitoring Endpoints ---
@app.get("/", tags=["Monitoring"])
async def read_root():
    """A simple root endpoint to confirm the app is running."""
    return {"message": "Welcome to the BookInn API!"}


@app.get("/health", tags=["Monitoring"])
async def health_check(session: AsyncSession = Depends(get_db_session)):
    """Health check endpoint that also verifies database connectivity."""
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        raise e
