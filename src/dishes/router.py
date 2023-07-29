from typing import List, Dict
from uuid import UUID

from fastapi import Depends, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.dishes.service import dish_service
from src.schemas import RequestDish, ResponseDish, ResponseMessage

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_dishes(target_submenu_id: UUID,
                         session: AsyncSession = Depends(get_async_session)
                         ) -> List[ResponseDish] | List[Dict]:
    """
    Get dishes list from db and return them.
    """
    return await dish_service.get_all_dishes(target_submenu_id, session)


@router.get("/{target_dish_id}", status_code=status.HTTP_200_OK,
            response_model=ResponseDish)
async def get_dish_by_id(target_dish_id: str | UUID,
                         session: AsyncSession = Depends(get_async_session)
                         ) -> ResponseDish:
    """
    Get dish from db and return it.

    target_dish_id: Current dish id.
    """
    return await dish_service.get_dish_by_id(target_dish_id, session)


@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=ResponseDish)
async def add_dish(target_submenu_id: str | UUID,
                   new_dish: RequestDish,
                   session: AsyncSession = Depends(get_async_session)
                   ) -> ResponseDish:
    """
    Add new dish to db and return it.

    target_submenu_id: Current submenu id.
    new_dish: Pydantic schema for request body.
    """
    return await dish_service.add_dish(target_submenu_id, new_dish, session)


@router.patch("/{target_dish_id}", status_code=status.HTTP_200_OK,
              response_model=ResponseDish)
async def update_dish(target_dish_id: str | UUID,
                      new_dish: RequestDish,
                      session: AsyncSession = Depends(get_async_session)
                      ) -> ResponseDish:
    """
    Update dish in db and return it.

    target_dish_id: Current dish id.
    new_dish: Pydantic schema for request body.
    """
    return await dish_service.update_dish(target_dish_id, new_dish, session)


@router.delete("/{target_dish_id}", status_code=status.HTTP_200_OK,
               response_model=ResponseMessage)
async def delete_dish(target_dish_id: str | UUID,
                      session: AsyncSession = Depends(get_async_session)
                      ) -> ResponseMessage:
    return await dish_service.delete_dish(target_dish_id, session)
