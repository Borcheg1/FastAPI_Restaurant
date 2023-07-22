from fastapi import APIRouter, Depends, status
from sqlalchemy import select, insert, func, distinct
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import Menus, Submenus, Dishes
from src.schemas import CreateMenu
from src.service import ConvertDataToJson

router = APIRouter(prefix="/api/v1/menus", tags=["Menus"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_menus(session: AsyncSession = Depends(get_async_session)):
    query = select(
        Menus.menu_id,
        Menus.title,
        Menus.description,
        func.count(distinct(Submenus.submenu_id)),
        func.count(Dishes.title)
    ).outerjoin(
        Submenus, Menus.menu_id == Submenus.menu_id
    ).outerjoin(
        Dishes, Submenus.submenu_id == Dishes.submenu_id
    ).group_by(
        Menus.menu_id
    )

    result = await session.execute(query)

    data = await ConvertDataToJson.get_menus(result)
    return data


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_menus(
        new_menu: CreateMenu,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = insert(Menus).values(**dict(new_menu))
        await session.execute(stmt)
        await session.commit()
        return {
            "status": "OK",
            "message": f"Creation of {new_menu.title} was successful!"
        }
    except IntegrityError as error:
        return {
            "status": "Error",
            "detail": error,
            "message": "Menu with this title already exists"
        }
