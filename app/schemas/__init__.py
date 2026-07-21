from schemas.user import *
from schemas.project import *
from schemas.task import *
from schemas.comment import *

UserDetailed.model_rebuild()
ProjectDetailed.model_rebuild()
TaskDetailed.model_rebuild()
CommentDetailed.model_rebuild()