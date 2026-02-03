from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_async_session
from app.schemas.auth import RegisterRequest, LoginRequest
from app.service.auth import AuthService
from app.service.security import SecurityService
from app.repository.users import UserRepository
from app.exceptions import InactiveUserError, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_service(db: AsyncSession = Depends(get_async_session)) -> AuthService:
    user_repo = UserRepository(db)
    return AuthService(user_repo)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(data: RegisterRequest, auth_service: AuthService = Depends(get_auth_service),):
    security = SecurityService()
    password_hash = security.hash_password(data.password)
    user = await auth_service.register_user(username=data.username, email=data.email, password_hash=password_hash)
    access_token = security.create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login")
async def login_user(data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        user = await auth_service.login_user(email=data.email, password=data.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    except InactiveUserError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    security = SecurityService()
    access_token = security.create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}
