from fastapi import FastAPI

from src.database import create_tables
from src.routers import router


app = FastAPI(title="Restaurant API")

app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def init_db() -> None:
    await create_tables()
