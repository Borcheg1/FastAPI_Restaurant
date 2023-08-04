from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.menus.service import menu_service
from src.schemas import BaseRequestModel, ResponseMenu, ResponseMessage

router = APIRouter()


@router.get('', status_code=status.HTTP_200_OK, response_model=list[ResponseMenu])
async def get_all_menus(
    session: AsyncSession = Depends(get_async_session),
) -> list[ResponseMenu]:
    """Get menus list from db and return them."""
    return await menu_service.get_all_menus(session)


@router.get(
    '/{target_menu_id}', status_code=status.HTTP_200_OK, response_model=ResponseMenu
)
async def get_menu_by_id(
    target_menu_id: UUID, session: AsyncSession = Depends(get_async_session)
) -> ResponseMenu:
    """Get menu from db and return it.

    target_menu_id: Current menu id.
    """
    return await menu_service.get_menu_by_id(target_menu_id, session)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=ResponseMenu)
async def add_menu(
    new_menu: BaseRequestModel, session: AsyncSession = Depends(get_async_session)
) -> ResponseMenu:
    """Add new submenu to db and return it.

    new_menu: Pydantic schema for request body.
    """
    return await menu_service.add_menu(new_menu, session)


@router.patch(
    '/{target_menu_id}', status_code=status.HTTP_200_OK, response_model=ResponseMenu
)
async def update_menu(
    target_menu_id: UUID,
    new_menu: BaseRequestModel,
    session: AsyncSession = Depends(get_async_session),
) -> ResponseMenu:
    """Update menu in db and return it.

    target_menu_id: Current menu id.
    new_menu: Pydantic schema for request body.
    """
    return await menu_service.update_menu(target_menu_id, new_menu, session)


@router.delete(
    '/{target_menu_id}', status_code=status.HTTP_200_OK, response_model=ResponseMessage
)
async def delete_menu(
    target_menu_id: UUID, session: AsyncSession = Depends(get_async_session)
) -> ResponseMessage:
    """Delete menu from db and return message.

    target_menu_id: Current menu id.
    """
    return await menu_service.delete_menu(target_menu_id, session)
