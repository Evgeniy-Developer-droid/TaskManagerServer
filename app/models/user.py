from datetime import datetime
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=True)
    full_name: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())

    settings: Mapped["UserSetting"] = relationship(
        back_populates="user", lazy="selectin"
    )
    subscription: Mapped["UserSubscription"] = relationship(
        back_populates="user", lazy="selectin"
    )
    auth_session: Mapped["AuthSession"] = relationship(back_populates="user")
    projects: Mapped["Project"] = relationship(back_populates="user")
    tasks: Mapped["Task"] = relationship(back_populates="user", lazy="selectin")


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    token: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())
    expired_at: Mapped[datetime] = mapped_column(DateTime())

    user: Mapped["User"] = relationship(back_populates="auth_session", lazy="selectin")


class UserSetting(Base):
    __tablename__ = "users_setting"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="settings")


class UserSubscription(Base):
    __tablename__ = "users_subscription"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    active_subscription: Mapped[bool] = mapped_column(default=False)
    cancel_subscription_at_period_end: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="subscription")
