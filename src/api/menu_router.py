from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session, get_redis_client
from src.schemas import BaseRequestModel, ResponseMenu, ResponseMessage
from src.service.menu_service import MenuService

router = APIRouter()
menu_service = MenuService()


@router.get(
    '', status_code=status.HTTP_200_OK, response_model=list[ResponseMenu]
)
async def get_all_menus(
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> list[ResponseMenu]:
    """Get from db list of all menus and return it.

    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
    """
    return await menu_service.get_all_menus(session, redis_client, background_tasks)


@router.get(
    '/{target_menu_id}', status_code=status.HTTP_200_OK,
    response_model=ResponseMenu
)
async def get_menu_by_id(
    target_menu_id: UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> ResponseMenu:
    """Get from db a specific menu by a specific ID.

    target_menu_id: Menu ID you want to get.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
    """
    return await menu_service.get_menu_by_id(
        session, redis_client, target_menu_id, background_tasks
    )


@router.post(
    '', status_code=status.HTTP_201_CREATED, response_model=ResponseMenu
)
async def add_menu(
    new_menu: BaseRequestModel,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> ResponseMenu:
    """Add a menu to db and return it.

    new_menu: Pydantic schema for request body.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
    """
    return await menu_service.add_menu(session, redis_client, new_menu, background_tasks)


@router.patch(
    '/{target_menu_id}', status_code=status.HTTP_200_OK,
    response_model=ResponseMenu
)
async def update_menu(
    target_menu_id: UUID,
    new_menu: BaseRequestModel,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> ResponseMenu:
    """Update in db a specific menu by a specific id.

    target_menu_id: Menu ID you want to update.
    new_menu: Pydantic schema for request body.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
    """
    return await menu_service.update_menu(
        session, redis_client, target_menu_id, new_menu, background_tasks
    )


@router.delete(
    '/{target_menu_id}', status_code=status.HTTP_200_OK,
    response_model=ResponseMessage
)
async def delete_menu(
    target_menu_id: UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> ResponseMessage:
    """Delete from db a specific menu by a specific id.

    target_menu_id: Menu ID you want to delete.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
    """
    return await menu_service.delete_menu(session, redis_client, target_menu_id, background_tasks)
