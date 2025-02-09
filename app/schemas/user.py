from typing import Any, Optional
from pydantic import BaseModel, EmailStr, field_validator


class AuthInSchema(BaseModel):
    username: Optional[EmailStr] = None
    email: Optional[EmailStr] = None
    password: str


class AuthOutSchema(BaseModel):
    token: str


class RegisterUserInSchema(BaseModel):
    email: EmailStr
    full_name: Optional[str]
    password: str

    @field_validator("password")
    @classmethod
    def password_validate(cls, v):
        if not v:
            raise ValueError("Empty password")
        return v


class UserSubscriptionSchema(BaseModel):
    active_subscription: bool
    cancel_subscription_at_period_end: bool


class UserSettingsSchema(BaseModel):
    id: int


class UserSchema(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: EmailStr
    is_active: bool
    settings: UserSettingsSchema
    subscription: Optional[UserSubscriptionSchema]
