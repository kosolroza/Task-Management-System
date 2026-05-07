from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.schemas import TaskCreate, TaskUpdate, TaskResponse, PaginatedTasks
from app.core.dependency import get_current_user
from app.models.models import User, StatusEnum
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.create_task(db, data, current_user)


@router.get("/", response_model=PaginatedTasks)
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[StatusEnum] = Query(None, description="Filter by status: todo | in_progress | done"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user ID"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    """
    GET /tasks?status=done&assigned_to=1&page=1&limit=10
    """
    return task_service.get_tasks(db, current_user, status, assigned_to, page, limit)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.get_task(db, task_id, current_user)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.update_task(db, task_id, data, current_user)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin can delete any task; users can only delete tasks in their projects."""
    return task_service.delete_task(db, task_id, current_user)
