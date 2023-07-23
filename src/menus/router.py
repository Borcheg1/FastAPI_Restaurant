from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert, func, distinct, update, delete
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

    result = await session.execute(query)

    response = await ConvertDataToJson.get_menus(result)
    return response


@router.get("/{target_menu_id}", status_code=status.HTTP_200_OK)
async def get_menu_by_id(
        target_menu_id: str | UUID,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(
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
    ).where(target_menu_id == Menus.id)

    result = await session.execute(query)

    response = await ConvertDataToJson.get_menu_by_id(result)

    if not response:
        raise HTTPException(status_code=404, detail='menu not found')
    return response


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_menu(
        new_menu: CreateMenu,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = insert(Menus).values(**dict(new_menu))
        await session.execute(stmt)
        await session.commit()

        query = select(
            Menus.id,
            Menus.title,
            Menus.description
        ).where(Menus.title == new_menu.title)

        result = await session.execute(query)
        response = await ConvertDataToJson.create_response(result)
        return response

    except IntegrityError as error:
        return {
            "status": "Error",
            "detail": error,
            "message": "Menu with this title already exists"
        }


@router.patch("/{target_menu_id}", status_code=status.HTTP_200_OK)
async def update_menu(
        target_menu_id: str | UUID,
        new_menu: CreateMenu,
        session: AsyncSession = Depends(get_async_session)
):
    new_menu_dict = dict(new_menu)
    try:
        stmt = update(Menus).where(target_menu_id == Menus.id).values(**new_menu_dict)
        await session.execute(stmt)
        await session.commit()

        new_menu_dict['id'] = target_menu_id

        response = new_menu_dict
        return response

    except IntegrityError as error:
        return {
            "status": "Error",
            "detail": error,
            "message": "Menu with this title already exists"
        }


@router.delete("/{target_menu_id}", status_code=status.HTTP_200_OK)
async def delete_menu(
        target_menu_id: str | UUID,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = delete(Menus).where(target_menu_id == Menus.id)
        await session.execute(stmt)
        await session.commit()
        return {
            "status": "OK",
            "message": f"Deleting was successful!"
        }
    except Exception as error:
        return {
            "status": "Error",
            "detail": error,
            "message": "Something went wrong!"
        }
