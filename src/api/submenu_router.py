from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.schemas import BaseRequestModel, ResponseMessage, ResponseSubmenu
from src.service.submenu_service import SubmenuService

router = APIRouter()
submenu_service = SubmenuService()


@router.get(
    '', status_code=status.HTTP_200_OK, response_model=list[ResponseSubmenu]
)
async def get_all_submenus(
    target_menu_id: UUID, session: AsyncSession = Depends(get_async_session)
) -> list[ResponseSubmenu]:
    """Get dishes list from db and return them."""
    return await submenu_service.get_all_submenus(session, target_menu_id)


@router.get(
    '/{target_submenu_id}',
    status_code=status.HTTP_200_OK,
    response_model=ResponseSubmenu,
)
async def get_submenu_by_id(
    target_menu_id: UUID,
    target_submenu_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> ResponseSubmenu:
    """Get submenu from db and return it.

    target_submenu_id: Current submenu id.
    """
    return await submenu_service.get_submenu_by_id(
        session, target_menu_id, target_submenu_id
    )


@router.post(
    '', status_code=status.HTTP_201_CREATED, response_model=ResponseSubmenu
)
async def add_submenu(
    target_menu_id: UUID,
    new_submenu: BaseRequestModel,
    session: AsyncSession = Depends(get_async_session),
) -> ResponseSubmenu:
    """Add new submenu to db and return it.

    target_menu_id: Current menu id.
    new_submenu: Pydantic schema for request body.
    """
    return await submenu_service.add_submenu(
        session, target_menu_id, new_submenu
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
    session: AsyncSession = Depends(get_async_session),
) -> ResponseSubmenu:
    """Update submenu in db and return it.

    target_submenu_id: Current submenu id.
    new_submenu: Pydantic schema for request body.
    """
    return await submenu_service.update_submenu(
        session, target_menu_id, target_submenu_id, new_submenu
    )


@router.delete(
    '/{target_submenu_id}',
    status_code=status.HTTP_200_OK,
    response_model=ResponseMessage,
)
async def delete_submenu(
    target_menu_id: UUID,
    target_submenu_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> ResponseMessage:
    """Delete submenu from db and return message.

    target_submenu_id: Current submenu id.
    """
    return await submenu_service.delete_submenu(
        session, target_menu_id, target_submenu_id
    )
