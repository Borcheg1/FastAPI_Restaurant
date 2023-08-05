import json

from fastapi import FastAPI

from src.database import create_tables
from src.router import main_router

app = FastAPI(title='Restaurant API')

app.include_router(main_router)


def custom_openapi():
    with open('openapi.json') as file:
        return json.load(file)


@app.on_event('startup')
async def init_db() -> None:
    """Initial Redis and recreate tables in db after app launch."""
    await create_tables()
