from typing import Any, Optional
from pydantic import BaseModel, field_validator


class SuccessResponseSchema(BaseModel):
    message: str
