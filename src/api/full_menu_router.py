from fastapi import APIRouter, BackgroundTasks, Depends, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session, get_redis_client
from src.schemas import ResponseFullMenu
from src.service.full_menu_service import FullMenuService

router = APIRouter()
full_menu_service = FullMenuService()


@router.get('', status_code=status.HTTP_200_OK)
async def get_full_menu(
    background_task: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_redis_client),
) -> list[ResponseFullMenu] | list:
    """Get from db list of menus with all submenus and dishes and return it.

    background_tasks: class instance FastAPI BackgroundTasks
    "tasks to be run after returning a response".
    session: Database session.
    redis_client: Redis session.
    """
    return await full_menu_service.get_full_menu(session, redis_client, background_task)
