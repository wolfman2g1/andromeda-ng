
from fastapi import status, APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
from loguru import logger
import uuid
from andromeda_ng.service.schema import UserOutput, UserSchema
from andromeda_ng.service.crud import user_service
from andromeda_ng.service.database import get_db
from andromeda_ng.service.utils import passwords
from andromeda_ng.service.libs import auth
from andromeda_ng.service.schema import Token, TokenData

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    try:
        logger.info(f"checking if user {form_data.username} exists")
        user = await user_service.get_user_by_username(db, form_data.username)
        if not user:
            logger.error(f"User does not exist: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect username or password")

        # Check password
        logger.info("checking if password is correct")
        if not passwords.verify_password(form_data.password, user.hashed_password):
            logger.error(f"Password is incorrect for user {user.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect username or password")
        if user.is_active == False:
            logger.error(f"User is not active: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect username or password")
        else:
            logger.info(f"Generating access token for user {user.username}")
            access_token = auth.create_access_token(
                data={"sub": str(user.id), "admin": user.admin, "username": user.username})
            logger.info(f"Access token generated for user {user.username}")
            return {"access_token": access_token, "token_type": "bearer", "username": user.username, "admin": user.admin}
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
