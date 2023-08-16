import json
from typing import Any

from fastapi import FastAPI

from src.database import create_tables, delete_cache
from src.router import main_router

app = FastAPI(title='Restaurant API')

app.include_router(main_router)


def custom_openapi() -> dict[str, Any]:
    """Convert openapi.json from json to dictionary"""
    with open('openapi.json') as file:
        return json.load(file)


@app.on_event('startup')
async def init_db() -> None:
    """Recreate tables in db and clear all cache in redis after app launch"""
    await create_tables()
    await delete_cache()


app.openapi = custom_openapi
