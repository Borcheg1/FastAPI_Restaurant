from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, distinct, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Dish, Submenu
from src.repository.menu_repository import MenuRepository
from src.schemas import BaseRequestModel, ResponseMessage, ResponseSubmenu


class SubmenuRepository:
    col = ('id', 'title', 'description', 'dishes_count')

    def __init__(self):
        self.menu_repository = MenuRepository()

    async def get_all(
        self, session: AsyncSession, menu_id: UUID
    ) -> list[ResponseSubmenu]:
        query = await session.execute(
            select(
                Submenu.id,
                Submenu.title,
                Submenu.description,
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)
            .where(Submenu.menu_id == menu_id)
            .group_by(Submenu.id)
        )
        rows = query.all()
        if not rows:
            return []

        menus = [ResponseSubmenu(**(dict(zip(self.col, row)))) for row in rows]
        return menus

    async def get_by_id(
        self, session: AsyncSession, menu_id: UUID, submenu_id: UUID
    ) -> ResponseSubmenu:
        query = await session.execute(
            select(
                Submenu.id,
                Submenu.title,
                Submenu.description,
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)
            .where(Submenu.menu_id == menu_id, Submenu.id == submenu_id)
            .group_by(Submenu.id)
        )
        row = query.first()

        if not row:
            raise HTTPException(status_code=404, detail='submenu not found')

        submenu = ResponseSubmenu(**dict(zip(self.col, row)))
        return submenu

    async def add(
        self, session: AsyncSession, menu_id: UUID,
        new_submenu: BaseRequestModel
    ) -> ResponseSubmenu:
        check_menu = await self.menu_repository.get_by_id(session, menu_id)
        if not check_menu:
            raise HTTPException(status_code=404, detail='submenu not found')

        try:
            await session.execute(
                insert(Submenu)
                .values(**dict(new_submenu, **{'menu_id': menu_id}))
            )
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=409, detail='This title already exists'
            )

        await session.commit()
        query = await session.execute(
            select(Submenu.id).where(Submenu.title == new_submenu.title)
        )
        submenu = ResponseSubmenu(**dict(new_submenu, **{
            'id': query.first()[0],
            'dishes_count': 0
        }))
        return submenu

    async def update(
        self, session: AsyncSession, menu_id: UUID, submenu_id: UUID,
        new_submenu: BaseRequestModel
    ) -> ResponseSubmenu:
        updating_submenu = await self.get_by_id(session, menu_id, submenu_id)

        if not updating_submenu:
            raise HTTPException(status_code=404, detail='submenu not found')

        updating_submenu.title = new_submenu.title
        updating_submenu.description = new_submenu.description

        try:
            await session.execute(
                update(Submenu).where(Submenu.id == submenu_id).values(
                    {
                        'id': updating_submenu.id,
                        'title': updating_submenu.title,
                        'description': updating_submenu.description
                    }
                )
            )
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=409, detail='This title already exists'
            )

        await session.commit()
        submenu = ResponseSubmenu(**dict(updating_submenu))
        return submenu

    async def delete(
        self, session: AsyncSession, menu_id: UUID, submenu_id: UUID
    ) -> ResponseMessage:
        check_menu = await self.menu_repository.get_by_id(session, menu_id)
        if not check_menu:
            raise HTTPException(status_code=404, detail='submenu not found')

        deleting_submenu = await session.execute(
            delete(Submenu).where(Submenu.id == submenu_id)
        )
        if deleting_submenu:
            await session.commit()
            return ResponseMessage(
                status=True, message='The submenu has been deleted'
            )
        else:
            raise HTTPException(status_code=404, detail='submenu not found')
