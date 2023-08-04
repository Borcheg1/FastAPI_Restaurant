from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, distinct, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Dish, Menu, Submenu
from src.schemas import BaseRequestModel, ResponseMenu, ResponseMessage


class MenuRepository:
    col = ('id', 'title', 'description', 'submenus_count', 'dishes_count')

    async def get_all(self, session: AsyncSession) -> list[ResponseMenu]:
        query = await session.execute(
            select(
                Menu.id,
                Menu.title,
                Menu.description,
                func.count(distinct(Submenu.id)).label('submenus_count'),
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .outerjoin(Submenu, Menu.id == Submenu.menu_id)
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)
            .group_by(Menu.id)
        )
        rows = query.all()
        menus = [ResponseMenu(**(dict(zip(self.col, row)))) for row in rows]
        return menus

    async def get_by_id(
        self, session: AsyncSession, menu_id: UUID
    ) -> ResponseMenu:
        query = await session.execute(
            select(
                Menu.id,
                Menu.title,
                Menu.description,
                func.count(distinct(Submenu.id)).label('submenus_count'),
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .outerjoin(Submenu, Menu.id == Submenu.menu_id)
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)
            .where(Menu.id == menu_id)
            .group_by(Menu.id)
        )
        row = query.first()

        if not row:
            raise HTTPException(status_code=404, detail='menu not found')

        menu = ResponseMenu(**dict(zip(self.col, row)))
        return menu

    @staticmethod
    async def add(
        session: AsyncSession, new_menu: BaseRequestModel
    ) -> ResponseMenu:
        try:
            await session.execute(insert(Menu).values(**dict(new_menu)))
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=409, detail='This title already exists'
            )

        await session.commit()
        query = await session.execute(select(Menu.id).where(
            Menu.title == new_menu.title
        ))
        menu = ResponseMenu(**dict(new_menu, **{
            'id': query.first()[0],
            'submenus_count': 0,
            'dishes_count': 0
        }))
        return menu

    async def update(
        self, session: AsyncSession, menu_id: UUID,
        new_menu: BaseRequestModel
    ) -> ResponseMenu:
        updating_menu = await self.get_by_id(session, menu_id)

        if not updating_menu:
            raise HTTPException(status_code=404, detail='menu not found')

        updating_menu.title = new_menu.title
        updating_menu.description = new_menu.description

        try:
            await session.execute(
                update(Menu).where(Menu.id == menu_id).values(
                    {
                        'id': updating_menu.id,
                        'title': updating_menu.title,
                        'description': updating_menu.description
                    }
                )
            )
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=409, detail='This title already exists'
            )

        await session.commit()
        menu = ResponseMenu(**dict(updating_menu))
        return menu

    @staticmethod
    async def delete(session: AsyncSession, menu_id: UUID) -> ResponseMessage:
        deleting_menu = await session.execute(
            delete(Menu).where(Menu.id == menu_id)
        )
        if deleting_menu:
            await session.commit()
            return ResponseMessage(
                status=True, message='The menu has been deleted'
            )
        else:
            raise HTTPException(status_code=404, detail='menu not found')
