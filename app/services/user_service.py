import os
import shutil
from typing import List

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.models import User, RoleEnum
from app.schemas.schemas import UserUpdate
from app.core.exception import UserNotFoundException, ForbiddenException
from app.core.config import settings


def get_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundException()
    return user


def get_all_users(db: Session) -> List[User]:
    return db.query(User).all()


def update_user(db: Session, user_id: int, data: UserUpdate, current_user: User) -> User:
    user = get_user(db, user_id)

    # Only admin or the owner can update
    if current_user.role != RoleEnum.admin and current_user.id != user_id:
        raise ForbiddenException()

    if data.username:
        user.username = data.username
    if data.email:
        user.email = data.email

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int, current_user: User) -> dict:
    user = get_user(db, user_id)

    if current_user.role != RoleEnum.admin and current_user.id != user_id:
        raise ForbiddenException()

    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}


def upload_avatar(db: Session, user_id: int, file: UploadFile, current_user: User) -> User:
    user = get_user(db, user_id)

    if current_user.role != RoleEnum.admin and current_user.id != user_id:
        raise ForbiddenException()

    # Validate file type
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Only JPEG/PNG/WEBP images allowed")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"user_{user_id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user.avatar_path = file_path
    db.commit()
    db.refresh(user)
    return user


# base64
# form data 
# superbase