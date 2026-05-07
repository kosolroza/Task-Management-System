from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.models import User
from app.schemas.schemas import UserCreate, Token
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exception import UnauthorizedException


def register_user(db: Session, data: UserCreate) -> User:
    # Check duplicates
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, username: str, password: str) -> Token:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedException("Incorrect username or password")

    token_data = {"sub": str(user.id)}
    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


def refresh_tokens(db: Session, refresh_token: str) -> Token:
    payload = decode_token(refresh_token)
    if payload is None:
        raise UnauthorizedException("Invalid or expired refresh token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise UnauthorizedException("User not found")

    token_data = {"sub": str(user.id)}
    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )
