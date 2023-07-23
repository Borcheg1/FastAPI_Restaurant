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

    @staticmethod
    async def get_submenus(result):
        json_data = []

        for row in result.fetchall():
            if not row:
                return json_data
            menu_id, title, desc, dishes_count = row[0], row[1], row[2], row[3]

            json_data.extend(
                [
                    {
                        "id": menu_id,
                        "title": title,
                        "description": desc,
                        "dishes_count": dishes_count
                    }
                ]
            )
        return json_data

    @staticmethod
    async def get_menu_by_id(result):
        row = result.fetchone()
        if not row:
            return None
        menu_id, title, desc, submenus_count, dishes_count = row[0], row[1], row[2], row[3], row[4]

        json_data = {
            "id": menu_id,
            "title": title,
            "description": desc,
            "submenus_count": submenus_count,
            "dishes_count": dishes_count
        }

        return json_data

    @staticmethod
    async def create_response(result):
        row = result.fetchone()
        if not row:
            return None
        current_id, title, desc = row[0], row[1], row[2]

        json_data = {
            "id": current_id,
            "title": title,
            "description": desc
        }

        return json_data

    @staticmethod
    async def get_submenu_by_id(result):
        row = result.fetchone()
        if not row:
            return None
        submenu_id, title, desc, dishes_count = row[0], row[1], row[2], row[3]

        json_data = {
            "id": submenu_id,
            "title": title,
            "description": desc,
            "dishes_count": dishes_count
        }

        return json_data
