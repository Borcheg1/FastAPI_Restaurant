from fastapi import FastAPI

from src.database import create_tables
from src.menus.router import router as menu_router
from src.submenus.router import router as submenu_router
from src.dishes.router import router as dish_router

app = FastAPI(title="Restaurant API")

app.include_router(
    menu_router,
    prefix="/api/v1/menus",
    tags=["Menu"]
)
app.include_router(
    submenu_router,
    prefix="/api/v1/menus/{target_menu_id}/submenus",
    tags=["Submenu"]
)
app.include_router(
    dish_router,
    prefix="/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes",
    tags=["Dish"]
)


@app.on_event("startup")
async def init_db() -> None:
    """
    Recreate tables in db after app launch
    """
    await create_tables()
