from typing import List, Dict
from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import Dishes
from src.schemas import RequestDish, ResponseDish, ResponseMessage

router = APIRouter()
main_query = select(
    Dishes.id,
    Dishes.title,
    Dishes.description,
    Dishes.price
).group_by(
    Dishes.id
)

col = Dishes.__table__.columns.keys()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_dishes(target_submenu_id: UUID, session: AsyncSession = Depends(get_async_session)
                         ) -> List[ResponseDish] | List[Dict]:
    """
    Get dishes list from db and return them.
    """
    result = await session.execute(main_query.where(Dishes.submenu_id == target_submenu_id))
    rows = result.fetchall()
    dishes = []
    for row in rows:
        dishes_dict = (dict(zip(col, row)))
        dishes_dict["price"] = str(dishes_dict["price"])
        dishes.append(ResponseDish(**dishes_dict))
    return dishes


@router.get("/{target_dish_id}", status_code=status.HTTP_200_OK, response_model=ResponseDish)
async def get_dish_by_id(target_dish_id: str | UUID,
                         session: AsyncSession = Depends(get_async_session)
                         ) -> ResponseDish:
    """
    Get dish from db and return it.

    target_dish_id: Current dish id.
    """
    query = main_query.where(target_dish_id == Dishes.id)
    result = await session.execute(query)
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail='dish not found')

    dish = dict(zip(col, row), **{'price': str(row[-1])})
    return ResponseDish(**dish)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponseDish)
async def add_dish(target_submenu_id: str | UUID,
                   new_dish: RequestDish,
                   session: AsyncSession = Depends(get_async_session)
                   ) -> ResponseDish:
    """
    Add new dish to db and return it.

    target_submenu_id: Current submenu id.
    new_dish: Pydantic schema for request body.
    """
    new_dish_dict = dict(new_dish, **{"submenu_id": target_submenu_id})
    stmt = insert(Dishes).values(**new_dish_dict)
    query = main_query.where(Dishes.title == new_dish.title)
    await session.execute(stmt)
    await session.commit()
    result = await session.execute(query)
    row = result.fetchone()
    dish = dict(zip(col, row), **{'price': str(row[-1])})
    return ResponseDish(**dish)


@router.patch("/{target_dish_id}", status_code=status.HTTP_200_OK, response_model=ResponseDish)
async def update_dish(target_dish_id: str | UUID,
                      new_dish: RequestDish,
                      session: AsyncSession = Depends(get_async_session)
                      ) -> ResponseDish:
    """
    Update dish in db and return it.

    target_dish_id: Current dish id.
    new_dish: Pydantic schema for request body.
    """
    new_dish_dict = dict(new_dish)
    stmt = update(Dishes).where(target_dish_id == Dishes.id).values(**new_dish_dict)
    await session.execute(stmt)
    await session.commit()

    new_dish_dict = {'id': target_dish_id, 'price': str(new_dish_dict['price']), **new_dish_dict}
    return ResponseDish(**new_dish_dict)


@router.delete("/{target_dish_id}", status_code=status.HTTP_200_OK, response_model=ResponseMessage)
async def delete_dish(target_dish_id: str | UUID,
                      session: AsyncSession = Depends(get_async_session)
                      ) -> ResponseMessage:
    """
    Delete dish from db and return message.

    target_dish_id: Current dish id.
    """
    stmt = delete(Dishes).where(target_dish_id == Dishes.id)
    await session.execute(stmt)
    await session.commit()
    return ResponseMessage(
        status=True,
        message="The dish has been deleted"
    )
