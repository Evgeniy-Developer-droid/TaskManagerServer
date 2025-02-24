from sqlalchemy.ext.asyncio.session import AsyncSession
from app.models.project import Project, Task
from typing_extensions import List
from sqlalchemy import select, insert, update, delete


async def create_project(data: dict, session: AsyncSession) -> Project:
    try:
        stmt = insert(Project).values(**data).returning(Project)
        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()
    except Exception as e:
        print(f"Error create project - {data}")


async def get_projects(user_id: int, session: AsyncSession) -> List[Project]:
    try:
        stmt = select(Project).where(Project.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        print(f"Error getting projects - {user_id}")


async def get_project(project_id: int, user_id: int, session: AsyncSession) -> Project:
    try:
        print(project_id, user_id)
        stmt = select(Project).where(
            Project.user_id == user_id, Project.id == project_id
        )
        result = await session.execute(stmt)
        return result.scalars().first()
    except Exception as e:
        print(f"Error getting project - user:{user_id} project:{project_id}")


async def delete_project(project_id: int, user_id: int, session: AsyncSession) -> bool:
    try:
        await delete_tasks(project_id, user_id, session)
        stmt = delete(Project).where(
            Project.user_id == user_id, Project.id == project_id, Project.is_default == False
        )
        result = await session.execute(stmt)
        await session.commit()
        return bool(result.rowcount)
    except Exception as e:
        print(f"Error deleting project - user:{user_id} project:{project_id}")
        return False


async def update_project(
    project_id: int, user_id: int, data: dict, session: AsyncSession
) -> Project:
    try:
        stmt = (
            update(Project)
            .values(**data)
            .where(Project.user_id == user_id, Project.id == project_id)
            .returning(Project)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()
    except Exception as e:
        print(
            f"Error updating project - user:{user_id} project:{project_id} data:{data}"
        )
        return False


# =====


async def create_task(data: dict, session: AsyncSession) -> Task:
    try:
        stmt = insert(Task).values(**data).returning(Task)
        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()
    except Exception as e:
        print(f"Error create Task - {data}")


async def get_tasks(user_id: int, project_id: int, session: AsyncSession) -> List[Task]:
    try:
        stmt = select(Task).where(
            Task.user_id == user_id, Task.project_id == project_id
        ).order_by(Task.created_at.desc())
        result = await session.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        print(f"Error getting Tasks - {user_id}")


async def get_task(
    task_id: int, project_id: int, user_id: int, session: AsyncSession
) -> Task:
    try:
        stmt = select(Task).where(
            Task.user_id == user_id, Task.id == task_id, Task.project_id == project_id
        )
        result = await session.execute(stmt)
        return result.scalars().first()
    except Exception as e:
        print(f"Error getting Task - user:{user_id} task:{task_id}")


async def delete_task(
    task_id: int, project_id: int, user_id: int, session: AsyncSession
) -> bool:
    try:
        stmt = delete(Task).where(
            Task.user_id == user_id, Task.id == task_id, Task.project_id == project_id
        )
        result = await session.execute(stmt)
        await session.commit()
        return bool(result.rowcount)
    except Exception as e:
        print(f"Error deleting Task - user:{user_id} project:{project_id}")
        return False


async def delete_tasks(project_id: int, user_id: int, session: AsyncSession) -> bool:
    try:
        stmt = delete(Task).where(
            Task.user_id == user_id, Task.project_id == project_id
        )
        result = await session.execute(stmt)
        await session.commit()
        return bool(result.rowcount)
    except Exception as e:
        print(f"Error deleting Tasks - user:{user_id} project:{project_id}")
        return False


async def update_task(
    task_id: int, project_id: int, user_id: int, data: dict, session: AsyncSession
) -> Task:
    try:
        stmt = (
            update(Task)
            .values(**data)
            .where(
                Task.user_id == user_id,
                Task.id == task_id,
                Task.project_id == project_id,
            )
            .returning(Task)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()
    except Exception as e:
        print(f"Error updating Task - user:{user_id} project:{project_id} data:{data}")
        return False
