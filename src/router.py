from fastapi import APIRouter

from src.api.dish_router import router as dish_router
from src.api.menu_router import router as menu_router
from src.api.submenu_router import router as submenu_router

main_router = APIRouter()

main_router.include_router(menu_router, prefix='/api/v1/menus', tags=['Menu'])
main_router.include_router(
    submenu_router, prefix='/api/v1/menus/{target_menu_id}/submenus',
    tags=['Submenu']
)
main_router.include_router(
    dish_router,
    prefix='/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes',
    tags=['Dish']
)
