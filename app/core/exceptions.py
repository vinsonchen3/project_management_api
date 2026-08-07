from fastapi import status


class APIException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class UserNotFoundError(APIException):
    def __init__(self, user_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"User with id {user_id} was not found.",
        )


class ProjectNotFoundError(APIException):
    def __init__(self, project_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Project with id {project_id} was not found.",
        )


class TaskNotFoundError(APIException):
    def __init__(self, task_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Task with id {task_id} was not found.",
        )


class CommentNotFoundError(APIException):
    def __init__(self, comment_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Comment with id {comment_id} was not found.",
        )


class DuplicateEmailError(APIException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=f"Email '{email}' is already in use.",
        )


class DuplicateUsernameError(APIException):
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=f"Username '{username}' is already in use.",
        )


class InvalidToken(APIException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid or expired authentication token.",
        )


class InvalidCredentials(APIException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid email or password.",
        )


class PermissionDeniedError(APIException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message="You do not have permission to perform this action.",
        )


class UserNotInProjectError(APIException):
    def __init__(self, user_id: int):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=f"User {user_id} is not a member of this project.",
        )
