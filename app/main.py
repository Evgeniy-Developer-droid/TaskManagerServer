from datetime import datetime, timedelta
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated
from fastapi import FastAPI, Depends, status, HTTPException
from app.database import get_session
from app import config
from app.schemas import user as user_schemas
from app.schemas import base as base_schemas
from app.schemas import project as project_schemas
from sqlalchemy.ext.asyncio.session import AsyncSession
from app import auth as auth_tools
from app.queries import user as user_queries
from app.models import user as user_models
from app.queries import project as project_queries
from app.models import project as project_models
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    debug=config.DEBUG,
    title="Task Manager",
    version="0.0.1",
    docs_url=(None if not config.DEBUG else "/docs"),
    redoc_url=(None if not config.DEBUG else "/redoc"),
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================AUTH===========================================


@app.post(
    "/auth/register", response_model=base_schemas.SuccessResponseSchema, tags=["auth"]
)
async def register_api(
    data: user_schemas.RegisterUserInSchema,
    db_session: AsyncSession = Depends(get_session),
):
    data_dict = data.model_dump()
    data_dict["password"] = await auth_tools.hash_password(data_dict["password"])
    data_dict["is_active"] = True
    user = await user_queries.create_user(data_dict, db_session)
    if not user:
        raise HTTPException(status_code=400, detail="Email already exist")
    # settings
    user_settings = await user_queries.create_user_settings(
        {"user_id": user.id}, db_session
    )
    # default project
    project = await project_queries.create_project(
        {"user_id": user.id, "name": "Default", "is_active": True, "is_default": True},
        db_session,
    )

    return {"message": "Success!"}


@app.post("/auth/token", response_model=user_schemas.AuthOutSchema, tags=["auth"])
async def login_api(
    data: user_schemas.AuthInSchema, db_session: AsyncSession = Depends(get_session)
):
    user = await user_queries.get_user_by_email(data.email, db_session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=404, detail="User is not active")
    if not await auth_tools.password_verify(data.password, user.password):
        raise HTTPException(status_code=404, detail="User not found")
    token_hex = uuid4().hex
    auth_session = await user_queries.create_auth_session(
        {
            "token": token_hex,
            "user_id": user.id,
            "expired_at": datetime.now()
            + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
        },
        db_session,
    )
    token = auth_tools.create_access_token({"sub": token_hex})
    return {"token": token}


@app.get(
    "/auth/logout", response_model=base_schemas.SuccessResponseSchema, tags=["auth"]
)
async def logout_api(
    auth_session: user_models.AuthSession = Depends(
        auth_tools.get_current_auth_session
    ),
    db_session: AsyncSession = Depends(get_session),
):
    await user_queries.delete_auth_session(auth_session.token, db_session)
    return {"message": "Success!"}


@app.post("/auth/swagger/token", response_model=dict, tags=["auth"])
async def login_swagger_api(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: AsyncSession = Depends(get_session),
):
    user = await user_queries.get_user_by_email(form_data.username, db_session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=404, detail="User is not active")
    if not await auth_tools.password_verify(form_data.password, user.password):
        raise HTTPException(status_code=404, detail="User not found")

    token_hex = uuid4().hex
    auth_session = await user_queries.create_auth_session(
        {
            "token": token_hex,
            "user_id": user.id,
            "expired_at": datetime.now()
            + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
        },
        db_session,
    )
    token = auth_tools.create_access_token({"sub": token_hex})

    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=user_schemas.UserSchema, tags=["user"])
async def me_api(
    user: user_models.User = Depends(auth_tools.get_current_active_user),
):
    return user


# ================================Project=================================


@app.post(
    "/projects", response_model=project_schemas.ProjectOutSchema, tags=["projects"]
)
async def create_project_api(
    data: project_schemas.ProjectInSchema,
    user: user_models.User = Depends(auth_tools.get_current_active_user),
    db_session: AsyncSession = Depends(get_session),
):
    data_dict = data.model_dump()
    data_dict["is_active"] = True
    data_dict["user_id"] = user.id
    project = await project_queries.create_project(data_dict, db_session)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Something was wrong"
        )
    return project


@app.get(
    "/projects",
    response_model=List[project_schemas.ProjectOutSchema],
    tags=["projects"],
)
async def get_projects_api(
    user: user_models.User = Depends(auth_tools.get_current_active_user),
    db_session: AsyncSession = Depends(get_session),
):
    print(user.id)
    projects = await project_queries.get_projects(user_id=user.id, session=db_session)
    return projects


@app.get(
    "/projects/{project_id:int}",
    response_model=project_schemas.ProjectOutSchema,
    tags=["projects"],
)
async def get_project_api(
    project_id: int,
    user: user_models.User = Depends(auth_tools.get_current_active_user),
    db_session: AsyncSession = Depends(get_session),
):
    print(project_id, user.id)
    project = await project_queries.get_project(
        project_id=project_id, user_id=user.id, session=db_session
    )
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return project


@app.put(
    "/projects/{project_id:int}",
    response_model=project_schemas.ProjectOutSchema,
    tags=["projects"],
)
async def update_project_api(
    project_id: int,
    data: project_schemas.ProjectUpdateInSchema,
    user: user_models.User = Depends(auth_tools.get_current_active_user),
    db_session: AsyncSession = Depends(get_session),
):
    data_dict = data.model_dump(exclude_none=True)
    project = await project_queries.update_project(
        project_id=project_id, user_id=user.id, data=data_dict, session=db_session
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Something was wrong"
        )
    return project


@app.delete(
    "/projects/{project_id:int}",
    response_model=base_schemas.SuccessResponseSchema,
    tags=["projects"],
)
async def delete_project_api(
    project_id: int,
    user: user_models.User = Depends(auth_tools.get_current_active_user),
    db_session: AsyncSession = Depends(get_session),
):
    await project_queries.delete_project(
        project_id=project_id, user_id=user.id, session=db_session
    )
    return {"message": "Success"}


# ================================Task=================================


@app.post(
    "/projects/{project_id:int}/tasks",
    response_model=project_schemas.TaskOutSchema,
    tags=["tasks"],
)
async def create_task_api(
    project_id: int,
    data: project_schemas.TaskInSchema,
    user: user_models.User = Depends(auth_tools.get_current_active_user),
    db_session: AsyncSession = Depends(get_session),
):
    project = await project_queries.get_project(
        project_id=project_id, user_id=user.id, session=db_session
    )
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    data_dict = data.model_dump()
    data_dict["user_id"] = user.id
    data_dict["project_id"] = project_id
    task = await project_queries.create_task(data_dict, db_session)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Something was wrong"
        )
    return task


@app.get(
    "/projects/{project_id:int}/tasks",
    response_model=List[project_schemas.TaskOutSchema],
    tags=["tasks"],
)
async def get_tasks_api(
    project_id: int,
    user: user_models.User = Depends(auth_tools.get_current_active_user),
    db_session: AsyncSession = Depends(get_session),
):
    tasks = await project_queries.get_tasks(
        user_id=user.id, project_id=project_id, session=db_session
    )
    return tasks


@app.get(
    "/projects/{project_id:int}/tasks/{task_id:int}",
    response_model=project_schemas.TaskOutSchema,
    tags=["tasks"],
)
async def get_task_api(
    project_id: int,
    task_id: int,
    user: user_models.User = Depends(auth_tools.get_current_active_user),
    db_session: AsyncSession = Depends(get_session),
):
    task = await project_queries.get_task(
        task_id=task_id, project_id=project_id, user_id=user.id, session=db_session
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return task


@app.put(
    "/projects/{project_id:int}/tasks/{task_id:int}",
    response_model=project_schemas.TaskOutSchema,
    tags=["tasks"],
)
async def update_task_api(
    project_id: int,
    task_id: int,
    data: project_schemas.TaskUpdateInSchema,
    user: user_models.User = Depends(auth_tools.get_current_active_user),
    db_session: AsyncSession = Depends(get_session),
):
    data_dict = data.model_dump(exclude_none=True)
    task = await project_queries.update_task(
        task_id=task_id,
        project_id=project_id,
        user_id=user.id,
        data=data_dict,
        session=db_session,
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Something was wrong"
        )
    return task


@app.delete(
    "/projects/{project_id:int}/tasks/{task_id:int}",
    response_model=base_schemas.SuccessResponseSchema,
    tags=["tasks"],
)
async def delete_task_api(
    project_id: int,
    task_id: int,
    user: user_models.User = Depends(auth_tools.get_current_active_user),
    db_session: AsyncSession = Depends(get_session),
):
    await project_queries.delete_task(
        task_id=task_id, project_id=project_id, user_id=user.id, session=db_session
    )
    return {"message": "Success"}
