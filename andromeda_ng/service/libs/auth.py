from datetime import datetime, timedelta, timezone
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from typing import Annotated, Any, Union, Optional
from uuid import UUID
from loguru import logger

from andromeda_ng.service.schema import TokenData
from andromeda_ng.service.settings import config

SECRET_KEY = config.SECRET_KEY.get_secret_value()
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRATION_MINUTES = config.ACCESS_TOKEN_EXPIRATION_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = config.REFRESH_TOKEN_EXPIRE_MINUTES
REFRESH_SECRET_KEY = config.REFRESH_SECRET_KEY.get_secret_value()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception: HTTPException) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("name")
        user_id: str = payload.get("sub")
        admin: bool = payload.get("admin")

        if not user_id:
            raise credentials_exception

        token_data = TokenData(
            username=username,
            id=UUID(user_id),
            admin=admin
        )
        return token_data
    except (JWTError, ValidationError) as e:
        logger.error(f"Token verification failed: {e}")
        raise credentials_exception


def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + \
            timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject), "scopes": []}
    encoded_jwt = jwt.encode(
        to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError as e:
        logger.error(f"Refresh token verification failed: {e}")
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return verify_access_token(token, credentials_exception)
