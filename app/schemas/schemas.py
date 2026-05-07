from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

from app.models.models import RoleEnum, StatusEnum


# ── Auth ──────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


class RefreshRequest(BaseModel):
    refresh_token: str


# ── User ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.user


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: RoleEnum
    avatar_path: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Project ───────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Task ──────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: int
    assigned_to: Optional[int] = None
    status: StatusEnum = StatusEnum.todo


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
    assigned_to: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: StatusEnum
    project_id: int
    assigned_to: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Pagination ────────────────────────────────────────────────────────────────

class PaginatedTasks(BaseModel):
    total: int
    page: int
    limit: int
    items: List[TaskResponse]
