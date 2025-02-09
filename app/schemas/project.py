from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from enum import Enum


class TaskStatus(str, Enum):
    new = "new"
    done = "done"


class TaskUpdateInSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskInSchema(BaseModel):
    name: str
    description: Optional[str] = ""


class TaskOutSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: TaskStatus
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime]


class ProjectUpdateInSchema(BaseModel):
    name: Optional[str] = None


class ProjectInSchema(BaseModel):
    name: str


class ProjectOutSchema(BaseModel):
    id: int
    name: str
    is_active: bool
    is_default: bool
    created_at: datetime
