from fastapi import status, APIRouter, Depends, HTTPException
from typing import List, Optional
from loguru import logger
import uuid
from andromeda_ng.service.schema import UserOutput, UserSchema
from andromeda_ng.service.crud import user_service
from andromeda_ng.service.database import get_db
from andromeda_ng.service.utils import passwords
router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/", response_model=UserOutput, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserSchema, db=Depends(get_db)):
    try:
        username = user_data.username.lower()
        check_user = await user_service.get_user_by_username(db, username)
        if check_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        user_data.username = username
        # chec password policy
        valid_password = passwords.verify_password_policy(
            user_data.password)
        if not valid_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password does not meet policy requirements")
        user = await user_service.create_user(db, user_data)
        return user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating user")


@router.get("/", response_model=List[UserOutput], status_code=status.HTTP_200_OK)
async def get_users(db=Depends(get_db)):
    try:
        logger.info("Getting all users")
        users = await user_service.get_all_users(db)
        return users
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting users")


@router.get("/{user_id}", response_model=UserOutput, status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: uuid.UUID, db=Depends(get_db)):
    try:

        user = await user_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        logger.info(f"Found User id: {user_id}")
        return user
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting user")


@router.put("/{user_id}", response_model=UserOutput, status_code=status.HTTP_200_OK)
async def update_user(user_id: uuid.UUID, user_data: UserSchema, db=Depends(get_db)):
    try:
        # check if user exists
        user = await user_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        # update user
        updated_user = await user_service.update_user(db, user_id, user_data)
        logger.info(f"User updated: {user_id}")
        return updated_user
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating user")


@router.delete("/{user_id}")
async def delete_user(user_id: uuid.UUID, db=Depends(get_db), status_code=status.HTTP_204_NO_CONTENT):
    try:
        # check if user exists
        user = await user_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        # delete user
        await user_service.delete_user(db, user_id)
        logger.info(f"User deleted: {user_id}")
        return {"message": "User deleted"}
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting user")
