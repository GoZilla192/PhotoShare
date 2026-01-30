from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.models.user import User

SECRET_KEY = "secretKey"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class SecurityService:
    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT decoded, user loading not implemented yet")
