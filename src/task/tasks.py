import asyncio
from typing import Any
from uuid import UUID

import pandas as pd
from _decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import INT
from sqlalchemy import UUID as sql_uuid
from sqlalchemy import Row, Sequence, insert, literal_column, select
from sqlalchemy.exc import IntegrityError

from src.cache.redis_cache import Cache
from src.database import async_session, create_tables, delete_cache, redis
from src.models import Dish, Menu, Submenu
from src.task.config import celery_app, menu_excel_path
from src.utils.excel_discounts import different_between_discounts

global_menu_id = None
global_submenu_id = None


@celery_app.task(name='check_excel')
def create_task() -> str:
    """Create a celery task and return string message about task status"""
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(compare_data())
    return result


async def _read_excel_file(path: str) -> tuple[list[Any], dict[str, list]]:
    """Protected function for read Excel file,
    prepare list of data to compare with db data and
    prepare dict of data to deleting None and adding to db.

    path: Excel file path.
    """
    data = pd.read_excel(path, header=None)
    excel_data_list = []
    excel_data_dict: dict = {
        'menus': [],
        'submenus': [],
        'dishes': [],
    }

    for idx, row in data.iterrows():
        row_data = row.values
        data_as_sql, item_category = await _create_data_for_bd(row_data)
        excel_data_list.append(data_as_sql)
        if item_category == 'menu':
            excel_data_dict['menus'].append(data_as_sql)
        elif item_category == 'submenu':
            excel_data_dict['submenus'].append(data_as_sql)
        elif item_category == 'dish':
            excel_data_dict['dishes'].append(data_as_sql[:5])

    return excel_data_list, excel_data_dict


async def _create_data_for_bd(row_data: tuple) -> tuple[Any, str]:
    """Protected function for preparing data to add to db and
    returning tuple of data and item category.
    Global variables are used to populate the bound id column.

    row_data: row of value from Excel file.
    """
    global global_menu_id
    global global_submenu_id

    data_as_sql = []

    if not pd.isnull(row_data[0]):
        data_as_sql.extend([
            UUID(row_data[0]),
            row_data[1],
            row_data[2] if not pd.isnull(row_data[2]) else 'null',
            None,
            None,
        ])
        global_menu_id = row_data[0]
        return tuple(data_as_sql), 'menu'
    else:
        if not pd.isnull(row_data[1]):
            data_as_sql.extend([
                UUID(row_data[1]),
                row_data[2],
                row_data[3] if not pd.isnull(row_data[3]) else 'null',
                None,
                UUID(global_menu_id),
            ])
            global_submenu_id = row_data[1]
            return tuple(data_as_sql), 'submenu'
        else:
            if not pd.isnull(row_data[2]):
                if len(row_data) == 7:
                    data_as_sql.extend([
                        UUID(row_data[2]),
                        row_data[3],
                        row_data[4] if not pd.isnull(row_data[4]) else 'null',
                        round(Decimal(row_data[5]), 2),
                        UUID(global_submenu_id),
                        row_data[6] if not pd.isnull(row_data[6]) else None,
                    ])
                    return tuple(data_as_sql), 'dish'
                else:
                    data_as_sql.extend([
                        UUID(row_data[2]),
                        row_data[3],
                        row_data[4] if not pd.isnull(row_data[4]) else 'null',
                        round(Decimal(row_data[5]), 2),
                        UUID(global_submenu_id),
                    ])
                    return tuple(data_as_sql), 'dish'
    return data_as_sql, 'menu'


async def _get_data_from_db() -> Sequence[Row[tuple[Any]]]:
    """Protected function for getting data from db or cache and
    if there is no data in cache, add it there.
    """
    query = select(
        Menu.id,
        Menu.title.label('title'),
        Menu.description,
        literal_column('null', type_=INT).label('price'),
        literal_column('null', type_=sql_uuid).label('some_id'),
    ).union_all(
        select(
            Submenu.id,
            Submenu.title.label('title'),
            Submenu.description,
            literal_column('null', type_=INT).label('price'),
            Submenu.menu_id,
        ).union_all(
            select(
                Dish.id,
                Dish.title.label('title'),
                Dish.description,
                Dish.price,
                Dish.submenu_id
            )
        )
    ).order_by('title')

    async with redis as client:
        cache = Cache()
        cache_data = await cache.get(client, 'db_data')

    if cache_data is not None:
        return cache_data

    async with async_session() as session:
        response = await session.execute(query)

    result = response.all()

    async with redis as client:
        cache = Cache()
        await cache.add(client, 'db_data', result)

    return result


async def compare_data() -> str:
    """Compares the data from the Excel file and the db and,
    if the data differs, deletes the db and fills it with data from the Excel file.
    """
    sql_data = await _get_data_from_db()

    excel_data_list, excel_data_dict = await _read_excel_file(menu_excel_path)
    excel_data_list_wo_discounts = [item[:5] for item in excel_data_list]
    excel_data_list_wo_discounts.sort(key=lambda x: x[1])

    if excel_data_list_wo_discounts == sql_data:
        result = await different_between_discounts(excel_data_list)
        return result
    else:
        if not excel_data_list_wo_discounts:
            await create_tables()
            await delete_cache()

            async with redis as client:
                cache = Cache()
                await cache.add(client, 'excel', excel_data_list)
            return 'Excel file is empty, database cleared'

        excel_data_dict_wo_none = await _delete_none(excel_data_dict)

        async with async_session() as session:
            try:
                await create_tables()
                await delete_cache()
                await session.execute(insert(Menu).values(excel_data_dict_wo_none['menus']))
                await session.execute(insert(Submenu).values(excel_data_dict_wo_none['submenus']))
                await session.execute(insert(Dish).values(excel_data_dict_wo_none['dishes']))
            except IntegrityError:
                await session.rollback()
                raise HTTPException(
                    status_code=409, detail='This title already exists'
                )
            await session.commit()

        async with redis as client:
            cache = Cache()
            await cache.add(client, 'excel', excel_data_list)
        return 'Changes detected between excel file and database, database updated'


async def _delete_none(excel_data_dict: dict) -> dict[str, list]:
    """Protected function for deleting None values from dictionary with Excel data
    and returning it.

    excel_data_dict: Dictionary with Excel data.
    """
    excel_data_dict_wo_none: dict = {
        'menus': [],
        'submenus': [],
        'dishes': [],
    }

    for key, value in excel_data_dict.items():
        for item in value:
            item_list = list(item)

            while None in item_list:
                item_list.remove(None)

            item_tuple = tuple(item_list)
            excel_data_dict_wo_none[key].append(item_tuple)

    return excel_data_dict_wo_none

#
# result = asyncio.run(compare_data())
# print(result)
