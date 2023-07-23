from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.dishes.router import DishVehicle
from src.schemas import CreateMenu, CreateSubmenu, CreateDish
from src.menus.router import MenuVehicle
from src.submenus.router import SubmenuVehicle


router = APIRouter(prefix="/menus")


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_menus(session: AsyncSession = Depends(get_async_session)):
    response = await MenuVehicle.get_all_menus(session)
    return response


@router.get("/{target_menu_id}", status_code=status.HTTP_200_OK)
async def get_menu_by_id(
        target_menu_id: str | UUID,
        session: AsyncSession = Depends(get_async_session)
):
    response = await MenuVehicle.get_menu_by_id(target_menu_id, session)
    return response


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_menu(
        new_menu: CreateMenu,
        session: AsyncSession = Depends(get_async_session)
):
    response = await MenuVehicle.add_menu(new_menu, session)
    return response


@router.patch("/{target_menu_id}", status_code=status.HTTP_200_OK)
async def update_menu(
        target_menu_id: str | UUID,
        new_menu: CreateMenu,
        session: AsyncSession = Depends(get_async_session)
):
    response = await MenuVehicle.update_menu(target_menu_id, new_menu, session)
    return response


@router.delete("/{target_menu_id}", status_code=status.HTTP_200_OK)
async def delete_menu(
        target_menu_id: str | UUID,
        session: AsyncSession = Depends(get_async_session)
):
    response = await MenuVehicle.delete_menu(target_menu_id, session)
    return response


@router.get("/{target_submenu_id}/submenus", status_code=status.HTTP_200_OK)
async def get_all_submenus(session: AsyncSession = Depends(get_async_session)):
    response = await SubmenuVehicle.get_all_submenus(session)
    return response


@router.get("/{target_menu_id}/submenus/{target_submenu_id}", status_code=status.HTTP_200_OK)
async def get_submenu_by_id(
        target_submenu_id: str | UUID,
        session: AsyncSession = Depends(get_async_session)
):
    response = await SubmenuVehicle.get_submenu_by_id(target_submenu_id, session)
    return response


@router.post("/{target_menu_id}/submenus", status_code=status.HTTP_201_CREATED)
async def add_menu(
        target_menu_id: str | UUID,
        new_submenu: CreateSubmenu,
        session: AsyncSession = Depends(get_async_session)
):
    response = await SubmenuVehicle.add_submenu(target_menu_id, new_submenu, session)
    return response


@router.patch("/{target_menu_id}/submenus/{target_submenu_id}", status_code=status.HTTP_200_OK)
async def update_submenu(
        target_submenu_id: str | UUID,
        new_menu: CreateSubmenu,
        session: AsyncSession = Depends(get_async_session)
):
    response = await SubmenuVehicle.update_submenu(target_submenu_id, new_menu, session)
    return response


@router.delete("/{target_menu_id}/submenus/{target_submenu_id}", status_code=status.HTTP_200_OK)
async def delete_submenu(
        target_submenu_id: str | UUID,
        session: AsyncSession = Depends(get_async_session)
):
    response = await SubmenuVehicle.delete_submenu(target_submenu_id, session)
    return response


@router.get("/{target_menu_id}/submenus/{target_submenu_id}/dishes", status_code=status.HTTP_200_OK)
async def get_all_dishes(session: AsyncSession = Depends(get_async_session)):
    response = await DishVehicle.get_all_dishes(session)
    return response


@router.get("/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}", status_code=status.HTTP_200_OK)
async def get_dish_by_id(
        target_dish_id: str | UUID,
        session: AsyncSession = Depends(get_async_session)
):
    response = await DishVehicle.get_dish_by_id(target_dish_id, session)
    print(response)
    return response


@router.post("/{target_menu_id}/submenus/{target_submenu_id}/dishes", status_code=status.HTTP_201_CREATED)
async def add_dish(
        target_submenu_id: str | UUID,
        new_dish: CreateDish,
        session: AsyncSession = Depends(get_async_session)
):
    response = await DishVehicle.add_dish(target_submenu_id, new_dish, session)
    return response


@router.patch("/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}", status_code=status.HTTP_200_OK)
async def update_dish(
        target_dish_id: str | UUID,
        new_dish: CreateDish,
        session: AsyncSession = Depends(get_async_session)
):
    response = await DishVehicle.update_dish(target_dish_id, new_dish, session)
    return response


@router.delete("/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}", status_code=status.HTTP_200_OK)
async def delete_dish(
        target_dish_id: str | UUID,
        session: AsyncSession = Depends(get_async_session)
):
    response = await DishVehicle.delete_dish(target_dish_id, session)
    return response
