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
    """Get from db list of all dishes and return it.

    target_menu_id: Menu ID that the submenu will belong to.
    target_submenu_id: Submenu ID that the dishes will belong to.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
    """
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
    """Get from db a specific dish by a specific ID and return it.

    target_menu_id: Menu ID that the submenu will belong to.
    target_submenu_id: Submenu ID that the dish will belong to.
    target_dish_id: Dish ID you want to get.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
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
    """
    Add a dish to db and return it.

    target_menu_id: Menu ID that the submenu will belong to.
    target_submenu_id: Submenu ID that the dish will belong to.
    new_dish: Pydantic schema for request body.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
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
    """
    Update in db a specific dish by a specific ID and return it.

    target_menu_id: Menu ID that the submenu will belong to.
    target_submenu_id: Submenu ID that the dish will belong to.
    target_dish_id: Dish ID you want to update.
    new_dish: Pydantic schema for request body.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
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
    """Delete from db a specific dish by a specific ID.

    target_menu_id: Menu ID that the submenu will belong to.
    target_submenu_id: Submenu ID that the dish will belong to.
    target_dish_id: Dish ID you want to delete.
    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
    """
    return await dish_service.delete_dish(
        session, redis_client, target_menu_id, target_submenu_id, target_dish_id, background_tasks
    )
