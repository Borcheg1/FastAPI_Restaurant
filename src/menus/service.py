from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import distinct, func, select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Menus, Submenus, Dishes
from src.schemas import ResponseMenu, BaseRequestModel, ResponseMessage


class MenuService:
    main_query = select(
        Menus.id,
        Menus.title,
        Menus.description,
        func.count(distinct(Submenus.id)),
        func.count(Dishes.title)
    ).outerjoin(
        Submenus, Menus.id == Submenus.menu_id
    ).outerjoin(
        Dishes, Submenus.id == Dishes.submenu_id
    ).group_by(
        Menus.id
    )

    col = Menus.__table__.columns.keys()

    @staticmethod
    async def check_exists_id_and_title(session: AsyncSession,
                                        target_id: UUID | str = None,
                                        title: str = None) -> None:
        query_check = select(Menus.id, Menus.title).where(target_id == Menus.id)
        query_title = select(Menus.title).where(title == Menus.title)

        if target_id:
            result = await session.execute(query_check)
            row = result.first()

            if not row:
                raise HTTPException(status_code=404, detail='menu not found')

            if title:
                if row[1] == title:
                    raise HTTPException(status_code=409,
                                        detail="This title already exists")

        if title and not target_id:
            result = await session.execute(query_title)
            if result.first():
                raise HTTPException(status_code=409,
                                    detail="This title already exists")

    async def get_all_menus(self, session: AsyncSession) -> List[ResponseMenu]:
        """
        Get menus list from db and return them.
        """
        result = await session.execute(self.main_query)
        rows = result.fetchall()
        menus = [ResponseMenu(**(dict(zip(self.col, row),
                                      **{"submenus_count": row[-2],
                                         "dishes_count": row[-1]})))
                 for row in rows]
        return menus

    async def get_menu_by_id(self, target_menu_id: UUID,
                             session: AsyncSession) -> ResponseMenu:
        """
        Get menu from db and return it.

        target_menu_id: Current menu id.
        """
        query = self.main_query.where(target_menu_id == Menus.id)
        result = await session.execute(query)
        row = result.first()

        if not row:
            raise HTTPException(status_code=404, detail='menu not found')

        menu = dict(zip(self.col, row), **{"submenus_count": row[-2],
                                           "dishes_count": row[-1]})
        return ResponseMenu(**menu)

    async def add_menu(self, new_menu: BaseRequestModel,
                       session: AsyncSession) -> ResponseMenu:
        """
        Add new submenu to db and return it.

        new_menu: Pydantic schema for request body.
        """
        stmt = insert(Menus).values(**dict(new_menu))
        query = self.main_query.where(Menus.title == new_menu.title)

        await self.check_exists_id_and_title(session, title=new_menu.title)
        await session.execute(stmt)
        await session.commit()
        result = await session.execute(query)
        row = result.fetchone()
        menu = dict(zip(self.col, row), **{"submenus_count": row[-2],
                                           "dishes_count": row[-1]})
        return ResponseMenu(**menu)

    async def update_menu(self, target_menu_id: UUID,
                          new_menu: BaseRequestModel,
                          session: AsyncSession) -> ResponseMenu:
        """
        Update menu in db and return it.

        target_menu_id: Current menu id.
        new_menu: Pydantic schema for request body.
        """
        stmt = update(Menus).where(
            target_menu_id == Menus.id).values(**dict(new_menu))
        query = self.main_query.where(target_menu_id == Menus.id)

        await self.check_exists_id_and_title(session,
                                             target_id=target_menu_id,
                                             title=new_menu.title)
        await session.execute(stmt)
        await session.commit()
        result = await session.execute(query)
        row = result.first()
        menu = dict(zip(self.col, row), **{"submenus_count": row[-2],
                                           "dishes_count": row[-1]})
        return ResponseMenu(**menu)

    async def delete_menu(self,
                          target_menu_id: UUID,
                          session: AsyncSession) -> ResponseMessage:
        """
        Delete menu from db and return message.

        target_menu_id: Current menu id.
        """
        stmt = delete(Menus).where(target_menu_id == Menus.id)

        await self.check_exists_id_and_title(session, target_id=target_menu_id)
        await session.execute(stmt)
        await session.commit()

        return ResponseMessage(
            status=True,
            message="The menu has been deleted"
        )


menu_service = MenuService()
