from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.core.exception import UnauthorizedException, ForbiddenException
from app.db.database import get_db
from app.models.models import User, RoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_token(token)
    if payload is None:
        raise UnauthorizedException("Invalid or expired token")

    user_id: int = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.admin:
        raise ForbiddenException("Admin access required")
    return current_user
