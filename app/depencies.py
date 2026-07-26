from typing import Annotated

from fastapi import Depends

from app.auth.auth_service import AuthService
from app.auth.dependencies import CurrentUser
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.comment_repository import CommentRepository

from app.services.user_service import UserService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.comment_service import CommentService

# ------------------------
# Database
# ------------------------

DBSession = Annotated[
    AsyncSession,
    Depends(get_db),
]


# ------------------------
# User
# ------------------------


def get_user_service(
    db: DBSession,
) -> UserService:
    return UserService(UserRepository(db))


UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]


# ------------------------
# Project
# ------------------------


def get_project_service(
    db: DBSession,
) -> ProjectService:
    return ProjectService(ProjectRepository(db))


ProjectServiceDep = Annotated[
    ProjectService,
    Depends(get_project_service),
]


# ------------------------
# Task
# ------------------------


def get_task_service(
    db: DBSession,
) -> TaskService:
    return TaskService(TaskRepository(db))


TaskServiceDep = Annotated[
    TaskService,
    Depends(get_task_service),
]


# ------------------------
# Comment
# ------------------------


def get_comment_service(
    db: DBSession,
) -> CommentService:
    return CommentService(CommentRepository(db))


CommentServiceDep = Annotated[
    CommentService,
    Depends(get_comment_service),
]


# ------------------------
# Authentication
# ------------------------


def get_auth_service(
    db: DBSession,
) -> AuthService:
    return AuthService(get_user_service(db))


AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service),
]
