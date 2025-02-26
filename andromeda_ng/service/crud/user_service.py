from loguru import logger
from andromeda_ng.service.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from andromeda_ng.service.schema import UserOutput, UserSchema
from andromeda_ng.service.models.user import User
import uuid
from andromeda_ng.service.utils.passwords import hash_password


async def create_user(db: Session, user_data: UserSchema):
    try:
        user_dict = user_data.model_dump()

        # Change password to hashed_password
        password = user_dict.pop("password")
        user_dict["hashed_password"] = hash_password(password)

        db_user = User(**user_dict)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User created: {db_user.id}")
        return db_user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        db.rollback()
        return None


async def get_user_by_username(db: Session, username: str):
    try:
        user = db.query(User).filter(User.username == username).first()
        return user
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None


async def get_user_by_id(db: Session, user_id: uuid.UUID):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None


async def update_user(db: Session, user_id: uuid.UUID, user_data: UserSchema):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        update_user = user.update(user_data.dict())
        db.commit()
        db.refresh(update_user)
        return user_data
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        db.rollback()
        return None


async def delete_user(db: Session, user_id: uuid.UUID):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        db.delete(user)
        db.commit()
        logger.info(f"User deleted: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        db.rollback()
        return {"error": "Error deleting user"}


async def get_all_users(db: Session):
    try:
        users = db.query(User).all()
        return users
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return None


async def get_user_by_email(db: Session, email: str):
    try:
        user = db.query(User).filter(User.email == email).first()
        return user
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None


async def get_user_by_id_(db: Session, user_id: uuid.UUID):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None
