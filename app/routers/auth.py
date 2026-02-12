from __future__ import annotations

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies import get_current_user, oauth2_scheme
from app.auth.service import AuthService
from app.core.exceptions import InactiveUserError, ConflictError, InvalidCredentialsError
from app.dependency.dependencies import auth_service as get_auth_service
from app.models import User
from app.schemas.register_schema import RegisterRequest, LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    data: RegisterRequest,
    auth: AuthService = Depends(get_auth_service),
):
    """
    Register new user.
    - First user may become admin (handled in AuthService).
    - Returns access_token.
    """
    try:
        _token = await auth.register(**data.model_dump())
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return {"access_token": _token, "token_type": "bearer"}



@router.post("/login")
async def login_user(
        data: LoginRequest,
        auth: AuthService = Depends(get_auth_service),
):
    """
    Login user and return access_token.
    AuthService handles password validation, inactive user, etc.
    """
    try:
        _token = await auth.login(email=data.email, password=data.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except InactiveUserError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return {"access_token": _token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
        current_user: User = Depends(get_current_user),
        _token: str = Depends(oauth2_scheme),  # <- беремо поточний bearer токен
        auth: AuthService = Depends(get_auth_service),
):
    """
    Logout = blacklist current token JTI until exp.
    Requires Authorization: Bearer <token>.
    """
    await auth.logout(_token)
    return

@router.post("/token")
async def token(
    form: OAuth2PasswordRequestForm = Depends(),
    auth: AuthService = Depends(get_auth_service),
):
    """
    OAuth2 password flow endpoint for Swagger "Authorize".
    Swagger field is 'username' but we interpret it as email.
    """
    try:
        _token = await auth.login(email=form.username, password=form.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    except InactiveUserError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    return {"access_token": _token, "token_type": "bearer"}