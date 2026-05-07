from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.models import Task, Project, User, RoleEnum, StatusEnum
from app.schemas.schemas import TaskCreate, TaskUpdate, PaginatedTasks, TaskResponse
from app.core.exception import TaskNotFoundException, ForbiddenException, ProjectNotFoundException


def _check_project_access(db: Session, project_id: int, current_user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ProjectNotFoundException()
    if current_user.role != RoleEnum.admin and project.owner_id != current_user.id:
        raise ForbiddenException()
    return project


def create_task(db: Session, data: TaskCreate, current_user: User) -> Task:
    _check_project_access(db, data.project_id, current_user)
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_tasks(
    db: Session,
    current_user: User,
    status: Optional[StatusEnum] = None,
    assigned_to: Optional[int] = None,
    page: int = 1,
    limit: int = 10,
) -> PaginatedTasks:
    query = db.query(Task)

    # Role-based data access
    if current_user.role != RoleEnum.admin:
        # Only tasks in projects owned by this user
        user_project_ids = [
            p.id for p in db.query(Project).filter(Project.owner_id == current_user.id).all()
        ]
        query = query.filter(Task.project_id.in_(user_project_ids))

    # Filters
    if status:
        query = query.filter(Task.status == status)
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    total = query.count()
    tasks = query.offset((page - 1) * limit).limit(limit).all()

    return PaginatedTasks(
        total=total,
        page=page,
        limit=limit,
        items=[TaskResponse.model_validate(t) for t in tasks],
    )


def get_task(db: Session, task_id: int, current_user: User) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise TaskNotFoundException()
    _check_project_access(db, task.project_id, current_user)
    return task


def update_task(db: Session, task_id: int, data: TaskUpdate, current_user: User) -> Task:
    task = get_task(db, task_id, current_user)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int, current_user: User) -> dict:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise TaskNotFoundException()

    # Admin can delete any task; users only their project's tasks
    if current_user.role != RoleEnum.admin:
        _check_project_access(db, task.project_id, current_user)

    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}
