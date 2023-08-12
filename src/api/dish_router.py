from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session, get_redis_client
from src.schemas import RequestDish, ResponseDish, ResponseMessage
from src.service.dish_service import DishService

router = APIRouter()
dish_service = DishService()


@router.get('', status_code=status.HTTP_200_OK)
async def get_all_dishes(
    target_menu_id: UUID,
    target_submenu_id: UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> list[ResponseDish]:
    """Get dishes list from db and return them."""
    return await dish_service.get_all_dishes(
        session, redis_client, target_menu_id, target_submenu_id, background_tasks
    )


@router.get(
    '/{target_dish_id}', status_code=status.HTTP_200_OK,
    response_model=ResponseDish
)
async def get_dish_by_id(
    target_menu_id: UUID,
    target_submenu_id: UUID,
    target_dish_id: UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> ResponseDish:
    """Get dish from db and return it.

    target_dish_id: Current dish id.
    """
    return await dish_service.get_dish_by_id(
        session, redis_client, target_menu_id, target_submenu_id, target_dish_id, background_tasks
    )


@router.post('', status_code=status.HTTP_201_CREATED,
             response_model=ResponseDish)
async def add_dish(
    target_menu_id: UUID,
    target_submenu_id: UUID,
    new_dish: RequestDish,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> ResponseDish:
    """Add new dish to db and return it.

    target_submenu_id: Current submenu id.
    new_dish: Pydantic schema for request body.
    """
    return await dish_service.add_dish(
        session, redis_client, target_menu_id, target_submenu_id, new_dish, background_tasks
    )


@router.patch(
    '/{target_dish_id}', status_code=status.HTTP_200_OK,
    response_model=ResponseDish
)
async def update_dish(
    target_menu_id: UUID,
    target_submenu_id: UUID,
    target_dish_id: UUID,
    new_dish: RequestDish,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> ResponseDish:
    """Update dish in db and return it.

    target_dish_id: Current dish id.
    new_dish: Pydantic schema for request body.
    """
    return await dish_service.update_dish(
        session, redis_client, target_menu_id, target_submenu_id,
        target_dish_id, new_dish, background_tasks
    )


@router.delete(
    '/{target_dish_id}', status_code=status.HTTP_200_OK,
    response_model=ResponseMessage
)
async def delete_dish(
    target_menu_id: UUID,
    target_submenu_id: UUID,
    target_dish_id: UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> ResponseMessage:
    return await dish_service.delete_dish(
        session, redis_client, target_menu_id, target_submenu_id, target_dish_id, background_tasks
    )
