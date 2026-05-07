from typing import List
from sqlalchemy.orm import Session

from app.models.models import Project, User, RoleEnum
from app.schemas.schemas import ProjectCreate, ProjectUpdate
from app.core.exception import ProjectNotFoundException, ForbiddenException


def create_project(db: Session, data: ProjectCreate, current_user: User) -> Project:
    project = Project(**data.model_dump(), owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: int, current_user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ProjectNotFoundException()

    # Regular users can only see their own projects
    if current_user.role != RoleEnum.admin and project.owner_id != current_user.id:
        raise ForbiddenException()

    return project


def get_projects(db: Session, current_user: User) -> List[Project]:
    if current_user.role == RoleEnum.admin:
        return db.query(Project).all()
    return db.query(Project).filter(Project.owner_id == current_user.id).all()


def update_project(db: Session, project_id: int, data: ProjectUpdate, current_user: User) -> Project:
    project = get_project(db, project_id, current_user)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int, current_user: User) -> dict:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ProjectNotFoundException()

    # Only admin or owner can delete
    if current_user.role != RoleEnum.admin and project.owner_id != current_user.id:
        raise ForbiddenException("Only admin or project owner can delete")

    db.delete(project)
    db.commit()
    return {"detail": "Project deleted"}
