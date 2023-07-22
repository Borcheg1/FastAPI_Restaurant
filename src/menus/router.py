from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import Menus

router = APIRouter(prefix="/menus", tags=["Menus"])


@router.get("")
async def get_all_menus(session: AsyncSession = Depends(get_async_session)):
    query = select(Menus)


@router.post("")
async def add_menus(session: AsyncSession = Depends(get_async_session)):
