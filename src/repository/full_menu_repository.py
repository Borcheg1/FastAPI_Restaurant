from sqlalchemy import Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Dish, Menu, Submenu
from src.schemas import ResponseFullDish, ResponseFullMenu, ResponseFullSubmenu


class FullMenuRepository:
    """A class to prepare data from db for all_data handlers.

    Class variable:
        dishes_subquery: Subquery for submenus_subquery.
        submenus_subquery: Subquery for query.
        query: Query to get all data from Menu, Submenu, Dish tables.

    Methods:
        get: Get data from db.
    """
    dishes_subquery = (
        select(
            Dish.submenu_id.label('submenu_id'),
            func.array_agg(func.row(Dish.id, Dish.title, Dish.description, Dish.price)).label('dishes_list'),
        ).group_by(Dish.submenu_id).subquery()
    )

    submenus_subquery = (
        select(
            Submenu.menu_id.label('menu_id'),
            func.array_agg(func.row(Submenu.id, Submenu.title, Submenu.description)).label('submenus_list'),
            dishes_subquery.c.dishes_list.label('dishes_list'),
        ).outerjoin(
            Submenu, Submenu.id == dishes_subquery.c.submenu_id, full=True
        ).group_by(
            Submenu.id,
            dishes_subquery.c.dishes_list
        ).subquery()
    )

    query = select(
        Menu.id,
        Menu.title,
        Menu.description,
        submenus_subquery.c.submenus_list.label('submenus_list'),
        submenus_subquery.c.dishes_list.label('dishes_list'),
    ).outerjoin(
        Menu, Menu.id == submenus_subquery.c.menu_id, full=True
    ).group_by(
        Menu.id,
        submenus_subquery.c.submenus_list,
        submenus_subquery.c.dishes_list
    ).order_by(Menu.id)

    async def get(self, session: AsyncSession) -> list[ResponseFullMenu] | list:
        """Get data from db, parse it, convert to json and return it.

        session: Database session.
        """
        result = await session.execute(self.query)

        full_menus_list = list()
        for row in result.all():
            full_menu_item = await self._parse_row(row)
            full_menus_list.append(full_menu_item)

        response = await self._create_json(full_menus_list)
        return response

    @staticmethod
    async def _parse_row(row: Row) -> ResponseFullMenu:
        """Protected method for parsing data from db to pydantic schema.

        row: One row of data from the database.
        """
        uuid, title, description, submenus_list, dishes_list = row

        full_menu_item = ResponseFullMenu(**{
            'id': uuid,
            'title': title,
            'description': description,
            'submenus_list': []
        })
        if submenus_list:
            full_menu_item.submenus_list.append(ResponseFullSubmenu(**{
                'id': submenus_list[0][0],
                'title': submenus_list[0][1],
                'description': submenus_list[0][2],
                'dishes_list': []
            }))
        if dishes_list:
            for dish in dishes_list:
                full_menu_item.submenus_list[0].dishes_list.append(ResponseFullDish(**{
                    'id': dish[0],
                    'title': dish[1],
                    'description': dish[2],
                    'price': str(round(dish[3], 2))
                }))
        return full_menu_item

    @staticmethod
    async def _create_json(full_menus_list: list[ResponseFullMenu]) -> list[ResponseFullMenu]:
        """Protected method for creating json from list of pydantic schemas.
        Combining items by common ID.

        full_menus_list: List of pydantic schemas "ResponseFullMenu".
        """
        full_menus_dict: dict = dict()
        for item in full_menus_list:
            if item.id in full_menus_dict:
                if item.submenus_list:
                    full_menus_dict[item.id].submenus_list.extend(item.submenus_list)
            elif not (item.id in full_menus_dict):
                full_menus_dict[item.id] = item
        result = [values for values in full_menus_dict.values()]
        return result
