from fastapi import FastAPI

from src.menus.router import router as menus_router


app = FastAPI(title="Restaurant API")

app.include_router(menus_router)
