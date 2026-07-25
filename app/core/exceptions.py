class UserNotFoundError(Exception):
    pass

class ProjectNotFoundError(Exception):
    pass

class TaskNotFoundError(Exception):
    pass

class CommentNotFoundError(Exception):
    pass

class DuplicateEmailError(Exception):
    pass

class DuplicateUsernameError(Exception):
    pass

class InvalidToken(Exception):
    pass

class InvalidCredentials(Exception):
    pass