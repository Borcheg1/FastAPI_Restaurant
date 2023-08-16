from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, distinct, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Dish, Submenu
from src.repository.menu_repository import MenuRepository
from src.schemas import BaseRequestModel, ResponseMessage, ResponseSubmenu


class SubmenuRepository:
    """A class to prepare data from db for submenu handlers.

        Class variable:
            col: Columns in a database table "Submenu" that are used when
            returning a response.

        Instance variable:
            menu_repository: A class instance to prepare data for menu handlers.

        Methods:
            get_all: Get from db all submenus.
            get_by_id: Get from db a specific submenu by a specific ID.
            add: Add a submenu to db.
            update: Update in db a specific submenu by a specific ID.
            delete: Delete from db a specific submenu by a specific ID.
        """
    col = ('id', 'title', 'description', 'dishes_count')

    def __init__(self):
        self.menu_repository = MenuRepository()

    async def get_all(
        self, session: AsyncSession, menu_id: UUID
    ) -> list[ResponseSubmenu]:
        """Get from db all submenus,
        convert it to list of pydantic schemas and return it.

        session: Database session.
        menu_id: Menu ID that the submenu will belong to.
        """
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
        """Get from db a specific submenu by a specific ID,
        convert it to pydantic schema and return it.

        session: Database session.
        menu_id: Menu ID that the submenu will belong to.
        submenu_id: Submenu ID you want to get.
        """
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
        """Add a submenu to db,
        convert submenu data to pydantic schema and return it.

        session: Database session.
        menu_id: Menu ID that the submenu will belong to.
        new_submenu: Pydantic schema for request body.
        """
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
        """Update in db a specific submenu by a specific ID,
        convert submenu data to pydantic schema and return it.

        session: Database session.
        menu_id: Menu ID that the submenu will belong to.
        submenu_id: Submenu ID you want to update.
        new_submenu: Pydantic schema for request body.
        """
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
        """Delete from db a specific submenu by a specific ID,
        and returning message with delete status.

        session: Database session.
        menu_id: Menu ID that the submenu will belong to.
        submenu_id: Submenu ID you want to delete.
        """
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
