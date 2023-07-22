from sqlalchemy import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session


class ConvertDataToJson:

    @staticmethod
    async def get_menus(result):
        json_data = []

        for row in result.fetchall():
            if not row:
                return json_data
            menu_id, title, desc, submenus_count, dishes_count = row[0], row[1], row[2], row[3], row[4]

            json_data.extend(
                [
                    {
                        "id": menu_id,
                        "title": title,
                        "description": desc,
                        "submenus_count": submenus_count,
                        "dishes_count": dishes_count
                    }
                ]
            )
        return json_data
