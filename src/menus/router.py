from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select, insert, func, distinct, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import Menus, Submenus, Dishes
from src.schemas import BaseRequestModel, ResponseMenu, ResponseMessage

router = APIRouter()

main_query = select(
    Menus.id,
    Menus.title,
    Menus.description,
    func.count(distinct(Submenus.id)),
    func.count(Dishes.title)
).outerjoin(
    Submenus, Menus.id == Submenus.menu_id
).outerjoin(
    Dishes, Submenus.id == Dishes.submenu_id
).group_by(
    Menus.id
)

col = Menus.__table__.columns.keys()


@router.get("", status_code=status.HTTP_200_OK, response_model=List[ResponseMenu])
async def get_all_menus(session: AsyncSession = Depends(get_async_session)
                        ) -> List[ResponseMenu]:
    """
    Get menus list from db and return them.
    """
    result = await session.execute(main_query)
    rows = result.fetchall()
    menus = [ResponseMenu(**(dict(zip(col, row), **{"submenus_count": row[-2], "dishes_count": row[-1]})))
             for row in rows]
    return menus


@router.get("/{target_menu_id}", status_code=status.HTTP_200_OK, response_model=ResponseMenu)
async def get_menu_by_id(target_menu_id: str | UUID,
                         session: AsyncSession = Depends(get_async_session)
                         ) -> ResponseMenu:
    """
    Get menu from db and return it.

    target_menu_id: Current menu id.
    """
    query = main_query.where(target_menu_id == Menus.id)
    result = await session.execute(query)
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail='menu not found')

    menu = dict(zip(col, row), **{"submenus_count": row[-2], "dishes_count": row[-1]})
    return ResponseMenu(**menu)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ResponseMenu)
async def add_menu(new_menu: BaseRequestModel,
                   session: AsyncSession = Depends(get_async_session)
                   ) -> ResponseMenu:
    """
    Add new submenu to db and return it.

    new_menu: Pydantic schema for request body.
    """
    stmt = insert(Menus).values(**dict(new_menu))
    query = main_query.where(Menus.title == new_menu.title)
    await session.execute(stmt)
    await session.commit()
    result = await session.execute(query)
    row = result.fetchone()
    menu = dict(zip(col, row), **{"submenus_count": row[-2], "dishes_count": row[-1]})
    return ResponseMenu(**menu)


@router.patch("/{target_menu_id}", status_code=status.HTTP_200_OK, response_model=ResponseMenu)
async def update_menu(target_menu_id: str | UUID,
                      new_menu: BaseRequestModel,
                      session: AsyncSession = Depends(get_async_session)
                      ) -> ResponseMenu:
    """
    Update menu in db and return it.

    target_menu_id: Current menu id.
    new_menu: Pydantic schema for request body.
    """
    stmt = update(Menus).where(target_menu_id == Menus.id).values(**dict(new_menu))
    query = main_query.where(target_menu_id == Menus.id)
    await session.execute(stmt)
    await session.commit()
    result = await session.execute(query)
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail='menu not found')

    menu = dict(zip(col, row), **{"submenus_count": row[-2], "dishes_count": row[-1]})
    return ResponseMenu(**menu)


@router.delete("/{target_menu_id}", status_code=status.HTTP_200_OK, response_model=ResponseMessage)
async def delete_menu(target_menu_id: str | UUID,
                      session: AsyncSession = Depends(get_async_session)
                      ) -> ResponseMessage:
    """
    Delete menu from db and return message.

    target_menu_id: Current menu id.
    """
    stmt = delete(Menus).where(target_menu_id == Menus.id)
    await session.execute(stmt)
    await session.commit()
    return ResponseMessage(
        status=True,
        message="The menu has been deleted"
    )
