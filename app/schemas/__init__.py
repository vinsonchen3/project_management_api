from app.schemas.user import *
from app.schemas.project import *
from app.schemas.task import *
from app.schemas.comment import *

UserDetailed.model_rebuild()
ProjectDetailed.model_rebuild()
TaskDetailed.model_rebuild()
CommentDetailed.model_rebuild()
