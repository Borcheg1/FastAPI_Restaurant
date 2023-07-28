from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select, insert, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import Submenus, Dishes
from src.schemas import BaseRequestModel, ResponseSubmenu, ResponseMessage

router = APIRouter()

main_query = select(
    Submenus.id,
    Submenus.title,
    Submenus.description,
    func.count(Dishes.title)
).outerjoin(
    Dishes, Submenus.id == Dishes.submenu_id
).group_by(
    Submenus.id
)

col = Submenus.__table__.columns.keys()


@router.get("", status_code=status.HTTP_200_OK, response_model=List[ResponseSubmenu])
async def get_all_submenus(target_menu_id: UUID,
                           session: AsyncSession = Depends(get_async_session)
                           ) -> List[ResponseSubmenu]:
    """
    Get dishes list from db and return them.
    """
    result = await session.execute(main_query.where(Submenus.menu_id == target_menu_id))
    rows = result.fetchall()
    submenus = [ResponseSubmenu(**(dict(zip(col, row), **{"dishes_count": row[-1]})))
                for row in rows]
    return submenus


@router.get("/{target_submenu_id}", status_code=status.HTTP_200_OK, response_model=ResponseSubmenu)
async def get_submenu_by_id(target_submenu_id: str | UUID,
                            session: AsyncSession = Depends(get_async_session)
                            ) -> ResponseSubmenu:
    """
    Get submenu from db and return it.

    target_submenu_id: Current submenu id.
    """
    query = main_query.where(target_submenu_id == Submenus.id)
    result = await session.execute(query)
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail='submenu not found')

    submenu = dict(zip(col, row), **{"dishes_count": row[-1]})
    return ResponseSubmenu(**submenu)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ResponseSubmenu)
async def add_menu(target_menu_id: str | UUID,
                   new_submenu: BaseRequestModel,
                   session: AsyncSession = Depends(get_async_session)
                   ) -> ResponseSubmenu:
    """
    Add new submenu to db and return it.

    target_menu_id: Current menu id.
    new_submenu: Pydantic schema for request body.
    """
    new_submenu_dict = dict(new_submenu, **{"menu_id": target_menu_id})
    query_check_title = select(Submenus).where(new_submenu.title == Submenus.title)
    stmt = insert(Submenus).values(**new_submenu_dict)
    query = main_query.where(Submenus.title == new_submenu.title)

    result_title = await session.execute(query_check_title)

    if result_title.first():
        raise HTTPException(status_code=409, detail="This title already exists")

    await session.execute(stmt)
    await session.commit()
    result = await session.execute(query)
    row = result.fetchone()
    submenu = dict(zip(col, row), **{"dishes_count": row[-1]})
    return ResponseSubmenu(**submenu)


@router.patch("/{target_submenu_id}", status_code=status.HTTP_200_OK, response_model=ResponseSubmenu)
async def update_submenu(target_submenu_id: str | UUID,
                         new_submenu: BaseRequestModel,
                         session: AsyncSession = Depends(get_async_session)
                         ) -> ResponseSubmenu:
    """
    Update submenu in db and return it.

    target_submenu_id: Current submenu id.
    new_submenu: Pydantic schema for request body.
    """
    stmt = update(Submenus).where(target_submenu_id == Submenus.id).values(**dict(new_submenu))
    query_check_id = select(Submenus).where(target_submenu_id == Submenus.id)
    query_check_title = select(Submenus).where(new_submenu.title == Submenus.title)
    query = main_query.where(target_submenu_id == Submenus.id)

    result_check_id = await session.execute(query_check_id)

    if not result_check_id.first():
        raise HTTPException(status_code=404, detail='submenu not found')

    result_title = await session.execute(query_check_title)

    if result_title.first():
        raise HTTPException(status_code=409, detail="This title already exists")

    await session.execute(stmt)
    await session.commit()
    result = await session.execute(query)
    row = result.first()
    submenu = dict(zip(col, row), **{"dishes_count": row[-1]})
    return ResponseSubmenu(**submenu)


@router.delete("/{target_submenu_id}", status_code=status.HTTP_200_OK, response_model=ResponseMessage)
async def delete_submenu(target_submenu_id: str | UUID,
                         session: AsyncSession = Depends(get_async_session)
                         ) -> ResponseMessage:
    """
    Delete submenu from db and return message.

    target_submenu_id: Current submenu id.
    """
    stmt = delete(Submenus).where(target_submenu_id == Submenus.id)
    query = select(Submenus).where(target_submenu_id == Submenus.id)
    result = await session.execute(query)
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail='submenu not found')

    await session.execute(stmt)
    await session.commit()

    return ResponseMessage(
        status=True,
        message="The submenu has been deleted"
    )
