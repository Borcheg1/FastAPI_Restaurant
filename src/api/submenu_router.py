from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session, get_redis_client
from src.schemas import BaseRequestModel, ResponseMessage, ResponseSubmenu
from src.service.submenu_service import SubmenuService

router = APIRouter()
submenu_service = SubmenuService()


@router.get(
    '', status_code=status.HTTP_200_OK, response_model=list[ResponseSubmenu]
)
async def get_all_submenus(
    target_menu_id: UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> list[ResponseSubmenu]:
    """Get from db list of all submenus and return it.

    target_menu_id: Menu ID that the submenu will belong to.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
    """
    return await submenu_service.get_all_submenus(
        session, redis_client, target_menu_id, background_tasks
    )


@router.get(
    '/{target_submenu_id}',
    status_code=status.HTTP_200_OK,
    response_model=ResponseSubmenu,
)
async def get_submenu_by_id(
    target_menu_id: UUID,
    target_submenu_id: UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> ResponseSubmenu:
    """Get from db a specific submenu by a specific ID.

    target_menu_id: Menu ID that the submenu will belong to.
    target_submenu_id: Submenu ID you want to get.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
    """
    return await submenu_service.get_submenu_by_id(
        session, redis_client, target_menu_id, target_submenu_id, background_tasks
    )


@router.post(
    '', status_code=status.HTTP_201_CREATED, response_model=ResponseSubmenu
)
async def add_submenu(
    target_menu_id: UUID,
    new_submenu: BaseRequestModel,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> ResponseSubmenu:
    """Add a submenu to db and return it.

    target_menu_id: Menu ID that the submenu will belong to.
    new_submenu: Pydantic schema for request body.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
    """
    return await submenu_service.add_submenu(
        session, redis_client, target_menu_id, new_submenu, background_tasks
    )


@router.patch(
    '/{target_submenu_id}',
    status_code=status.HTTP_200_OK,
    response_model=ResponseSubmenu,
)
async def update_submenu(
    target_menu_id: UUID,
    target_submenu_id: UUID,
    new_submenu: BaseRequestModel,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> ResponseSubmenu:
    """Update in db a specific submenu by a specific ID.

    target_menu_id: Menu ID that the submenu will belong to.
    target_submenu_id: Submenu ID you want to update.
    new_submenu: Pydantic schema for request body.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
    """
    return await submenu_service.update_submenu(
        session, redis_client, target_menu_id, target_submenu_id, new_submenu, background_tasks
    )


@router.delete(
    '/{target_submenu_id}',
    status_code=status.HTTP_200_OK,
    response_model=ResponseMessage,
)
async def delete_submenu(
    target_menu_id: UUID,
    target_submenu_id: UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> ResponseMessage:
    """Delete from db a specific submenu by a specific ID.

    target_menu_id: Menu ID that the submenu will belong to.
    target_submenu_id: Submenu ID you want to delete.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
    """
    return await submenu_service.delete_submenu(
        session, redis_client, target_menu_id, target_submenu_id, background_tasks
    )
