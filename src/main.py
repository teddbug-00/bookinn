from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.router import router as auth_router
from src.database import get_db_session
from src.exceptions import AppError
from src.users.router import router as users_router

# Create the main FastAPI application instance
app = FastAPI(
    title="BookInn API",
    description="API for the BookInn service.",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(users_router)


@app.exception_handler(AppError)
async def app_exception_handler(request: Request, exc: AppError):
    """Global handler to catch all AppError exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )


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
        # Re-raise the error to let FastAPI's default handlers manage it.
        raise e
