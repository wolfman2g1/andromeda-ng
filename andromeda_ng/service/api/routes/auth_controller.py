
from fastapi import status, APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
from loguru import logger
import uuid

from pydantic import EmailStr
from andromeda_ng.service.schema import PasswordResetRequest
from andromeda_ng.service.crud import user_service
from andromeda_ng.service.database import get_db
from andromeda_ng.service.utils import passwords
from andromeda_ng.service.libs import auth, email
from andromeda_ng.service.schema import Token, TokenData

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    try:
        logger.info(f"checking if user {form_data.username} exists")
        user = await user_service.get_user_by_username(db, form_data.username)
        if not user:
            logger.error(f"User does not exist: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Incorrect username or password"
            )

        # Check password
        logger.info("checking if password is correct")
        if not passwords.verify_password(form_data.password, user.hashed_password):
            logger.error(f"Password is incorrect for user {user.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Incorrect username or password"
            )

        if not user.is_active:
            logger.error(f"User is not active: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Incorrect username or password"
            )

        # Generate both access and refresh tokens
        access_token = auth.create_access_token(
            data={
                "sub": str(user.id),
                "admin": user.admin,
                "username": user.username
            }
        )
        refresh_token = auth.create_refresh_token(subject=str(user.id))

        logger.info(f"Tokens generated for user {user.username}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "username": user.username,
            "admin": user.admin
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# verfication of token


@router.get("/verifytoken/{token}", response_model=TokenData, status_code=status.HTTP_200_OK)
async def verify_token(token: str):
    try:
        logger.info("Verifying token")
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token_data = auth.verify_access_token(token, credentials_exception)
        logger.info("Token verified")
        return token_data
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

# refresh token


@router.post("/refresh/{token}", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(token: str, db=Depends(get_db)):
    try:
        logger.info("Refreshing token")
        user_id = auth.verify_refresh_token(token)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

        # Fetch user from database to get current admin status
        user = await user_service.get_user_by_id(db, user_id)
        if not user:
            logger.error(f"User not found for id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

        if not user.is_active:
            logger.error(f"Inactive user attempting token refresh: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive")

        # Generate both new access and refresh tokens
        access_token = auth.create_access_token(
            data={
                "sub": str(user.id),
                "admin": user.admin,
                "username": user.username
            }
        )
        refresh_token = auth.create_refresh_token(subject=str(user.id))

        logger.info(f"Tokens refreshed for user {user.username}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "username": user.username,
            "admin": user.admin
        }
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(email: EmailStr, db=Depends(get_db)):
    """
    Send password reset email to user including token
    """
    try:
        logger.info(f"Checking if email {email} exists")
        user = await user_service.get_user_by_email(db, email)
        # don't return any information if the email doesn't exist
        # Generate password reset token
        if user:
            reset_token = auth.create_password_reset_token(str(user.id))

        # Send password reset email
            await email.send_password_reset_email(
                email_to=email,
                username=user.username,
                reset_token=reset_token
            )

            logger.info(f"Password reset email sent to {email}")
            return {"message": "Password reset email sent"}
        else:
            logger.error(f"Email {email} not found")
            return {"message": "Password reset email sent"}
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(reset_data: PasswordResetRequest, db=Depends(get_db)):
    """Reset user password using reset token"""
    try:
        logger.info("Verifying password reset token")
        user_id = auth.verify_password_reset_token(reset_data.token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired reset token"
            )

        # Fetch user from database
        user = await user_service.get_user_by_id(db, user_id)
        if not user:
            logger.error(f"User not found for id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Validate password policy
        valid, message = passwords.verify_password_policy(
            reset_data.new_password)
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password policy error: {message}"
            )

        # Hash and update password
        hashed_password = passwords.hash_password(reset_data.new_password)
        success = await user_service.update_user_password(db, user_id, hashed_password)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )

        logger.info(f"Password reset successful for user {user.username}")
        return {"message": "Password reset successful"}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )
