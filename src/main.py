from fastapi import FastAPI

from src.database import create_tables
from src.menus.router import router as menus_router


app = FastAPI(title="Restaurant API")

app.include_router(menus_router)


@app.on_event("startup")
async def init_db() -> None:
    await create_tables()
