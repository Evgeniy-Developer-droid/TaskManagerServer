from typing_extensions import Annotated
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app import config
from app.database import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.queries import user as user_queries
from app.schemas import user as user_schemas
from app.models import user as user_models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/swagger/token")


async def hash_password(password: str):
    return pwd_context.hash(password)


async def password_verify(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


async def get_current_auth_session(
    token: str = Depends(oauth2_scheme), db_session: AsyncSession = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        token_session: str = payload.get("sub")
        if token_session is None:
            raise credentials_exception
        auth_session = await user_queries.get_auth_session(token_session, db_session)
        if not auth_session:
            raise credentials_exception
        return auth_session
    except JWTError:
        raise credentials_exception


async def get_current_user(
    auth_session: str = Depends(get_current_auth_session), db_session: AsyncSession = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if not auth_session:
            raise credentials_exception
        return auth_session.user
    except JWTError:
        raise credentials_exception


async def get_current_active_user(
    current_user: Annotated[user_models.User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
