from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Submenus, Dishes
from src.schemas import BaseRequestModel, ResponseMessage, ResponseSubmenu


class SubmenuService:
    main_query = select(
        Submenus.id,
        Submenus.title,
        Submenus.description,
        func.count(Dishes.title)
    ).outerjoin(
        Dishes, Submenus.id == Dishes.submenu_id
    ).group_by(
        Submenus.id
    )

    col = Submenus.__table__.columns.keys()

    @staticmethod
    async def check_exists_id_and_title(session: AsyncSession,
                                        target_id: UUID | str = None,
                                        title: str = None) -> None:
        query_check = select(
            Submenus.id, Submenus.title).where(target_id == Submenus.id)
        query_title = select(Submenus.title).where(title == Submenus.title)

        if target_id:
            result = await session.execute(query_check)
            row = result.first()

            if not row:
                raise HTTPException(status_code=404, detail='submenu not found')

            if title:
                if row[1] == title:
                    raise HTTPException(status_code=409,
                                        detail="This title already exists")

        if title and not target_id:
            result = await session.execute(query_title)
            if result.first():
                raise HTTPException(status_code=409,
                                    detail="This title already exists")

    async def get_all_submenus(self, target_menu_id: UUID,
                               session: AsyncSession) -> List[ResponseSubmenu]:
        """
        Get dishes list from db and return them.
        """
        result = await session.execute(
            self.main_query.where(Submenus.menu_id == target_menu_id))
        rows = result.fetchall()
        submenus = [ResponseSubmenu(
            **(dict(zip(self.col, row), **{"dishes_count": row[-1]})))
                    for row in rows]
        return submenus

    async def get_submenu_by_id(self, target_submenu_id: UUID,
                                session: AsyncSession) -> ResponseSubmenu:
        """
        Get submenu from db and return it.

        target_submenu_id: Current submenu id.
        """
        query = self.main_query.where(target_submenu_id == Submenus.id)
        result = await session.execute(query)
        row = result.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail='submenu not found')

        submenu = dict(zip(self.col, row), **{"dishes_count": row[-1]})
        return ResponseSubmenu(**submenu)

    async def add_submenu(self, target_menu_id: UUID,
                          new_submenu: BaseRequestModel,
                          session: AsyncSession) -> ResponseSubmenu:
        """
        Add new submenu to db and return it.

        target_menu_id: Current menu id.
        new_submenu: Pydantic schema for request body.
        """
        new_submenu_dict = dict(new_submenu, **{"menu_id": target_menu_id})
        stmt = insert(Submenus).values(**new_submenu_dict)
        query = self.main_query.where(Submenus.title == new_submenu.title)

        await self.check_exists_id_and_title(session, title=new_submenu.title)
        await session.execute(stmt)
        await session.commit()
        result = await session.execute(query)
        row = result.fetchone()
        submenu = dict(zip(self.col, row), **{"dishes_count": row[-1]})
        return ResponseSubmenu(**submenu)

    async def update_submenu(self, target_submenu_id: UUID,
                             new_submenu: BaseRequestModel,
                             session: AsyncSession) -> ResponseSubmenu:
        """
        Update submenu in db and return it.

        target_submenu_id: Current submenu id.
        new_submenu: Pydantic schema for request body.
        """
        stmt = update(Submenus).where(
            target_submenu_id == Submenus.id).values(**dict(new_submenu))
        query = self.main_query.where(target_submenu_id == Submenus.id)

        await self.check_exists_id_and_title(session,
                                             target_id=target_submenu_id,
                                             title=new_submenu.title)
        await session.execute(stmt)
        await session.commit()
        result = await session.execute(query)
        row = result.first()
        submenu = dict(zip(self.col, row), **{"dishes_count": row[-1]})
        return ResponseSubmenu(**submenu)

    async def delete_submenu(self, target_submenu_id: str | UUID,
                             session: AsyncSession) -> ResponseMessage:
        """
        Delete submenu from db and return message.

        target_submenu_id: Current submenu id.
        """
        stmt = delete(Submenus).where(target_submenu_id == Submenus.id)

        await self.check_exists_id_and_title(session,
                                             target_id=target_submenu_id)

        await session.execute(stmt)
        await session.commit()

        return ResponseMessage(
            status=True,
            message="The submenu has been deleted"
        )


submenu_service = SubmenuService()
