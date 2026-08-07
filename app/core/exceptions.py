class APIException(Exception):
    pass


class UserNotFoundError(APIException):
    pass


class ProjectNotFoundError(APIException):
    pass


class TaskNotFoundError(APIException):
    pass


class CommentNotFoundError(APIException):
    pass


class DuplicateEmailError(APIException):
    pass


class DuplicateUsernameError(APIException):
    pass


class InvalidToken(APIException):
    pass


class InvalidCredentials(APIException):
    pass


class PermissionDeniedError(APIAPIException):
    pass


class UserNotInProjectError(APIException):
    pass
