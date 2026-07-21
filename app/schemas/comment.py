from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class CommentBase(BaseModel):
    content: str = Field(min_length=1, description="Comment content")
    
class CommentCreate(CommentBase):
    task_id: int 

class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_posted: datetime
    author_id: int 
    task_id: int