from typing import Annotated, Optional
from datetime import datetime

from pydantic import BaseModel, Field

from ..models.task import Priority, TaskStatus


class TaskCreate(BaseModel):
    name: Annotated[str, Field(max_length=128, min_length=3)]
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    due_date: datetime
    priority: Priority = Priority.PRIORITY05
    category_id: int


class TaskResponse(BaseModel):
    task_id: int
    name: Annotated[str, Field(max_length=128, min_length=3)]
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    due_date: datetime
    status: TaskStatus
    priority: Priority
    category_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class TaskUpdate(BaseModel):
    name: Optional[Annotated[str, Field(max_length=128, min_length=3)]] = None
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    category_id: Optional[int] = None
