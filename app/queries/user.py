from sqlalchemy.ext.asyncio.session import AsyncSession
from app.models.user import User, AuthSession, UserSetting, UserSubscription
from sqlalchemy import select, insert, update, delete


async def create_auth_session(data: dict, session: AsyncSession) -> AuthSession:
    try:
        stmt = insert(AuthSession).values(**data).returning(AuthSession)
        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()
    except Exception as e:
        print(f"Error create auth session - {data}")


async def get_auth_session(token, session: AsyncSession) -> AuthSession:
    try:
        stmt = select(AuthSession).where(AuthSession.token == token)
        result = await session.execute(stmt)
        return result.scalars().first()
    except Exception as e:
        print(f"Error getting auth session - {token}")


async def delete_auth_session(token, session: AsyncSession) -> bool:
    try:
        stmt = delete(AuthSession).where(AuthSession.token == token)
        result = await session.execute(stmt)
        return bool(result.rowcount)
    except Exception as e:
        print(f"Error deleting auth session - {token}")
        return False


async def create_user(data: dict, session: AsyncSession) -> User:
    try:
        stmt = insert(User).values(**data).returning(User)
        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()
    except Exception as e:
        print(f"Error create user -{data}")


async def get_user_by_id(user_id: int, session: AsyncSession) -> User:
    try:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()
    except Exception as e:
        print(f"Error gretting user(id) -{user_id}")


async def get_user_by_email(email: str, session: AsyncSession) -> User:
    try:
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalars().first()
    except Exception as e:
        print(f"Error gretting user(email) -{email}")


async def create_user_settings(data: dict, session: AsyncSession) -> UserSetting:
    try:
        stmt = insert(UserSetting).values(**data).returning(UserSetting)
        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()
    except Exception as e:
        print(f"Error create user settings - {data}")
