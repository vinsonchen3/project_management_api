from enum import Enum 

class TaskStatus(Enum):
    TO_DO = "To Do"
    IN_PROGRESS = "In Progress"
    UNDER_REVIEW = "Under Review"
    COMPLETED = "Completed"
