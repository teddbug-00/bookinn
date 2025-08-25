from typing import Annotated

from fastapi import APIRouter, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import services
from src.auth.schemas import Token, LoginRequest
from src.database import get_db_session

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token, summary="Login for standard users")
async def login_with_json(
        login_data: LoginRequest,
        session: AsyncSession = Depends(get_db_session),
):
    """Authenticates a user with email and password via JSON and returns a token."""
    return await services.authenticate_user_and_get_tokens(
        email=login_data.email, password=login_data.password, session=session
    )


@router.post("/token", response_model=Token, summary="Login for Swagger UI")
async def login_for_access_token_for_swagger(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: AsyncSession = Depends(get_db_session),
):
    """Authenticates a user with form data (for Swagger UI) and returns a token."""
    return await services.authenticate_user_and_get_tokens(
        email=form_data.username, password=form_data.password, session=session
    )


@router.post("/refresh", response_model=Token, summary="Refresh access token")
async def refresh_access_token(
        refresh_token: str = Body(..., embed=True),
        session: AsyncSession = Depends(get_db_session),
):
    """
    Generates a new access and refresh token from a valid refresh token.
    """
    return await services.refresh_tokens(refresh_token, session)
