from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ProjectNotFoundException(HTTPException):
    def __init__(self, detail: str = "Project not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class TaskNotFoundException(HTTPException):
    def __init__(self, detail: str = "Task not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
