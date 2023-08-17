import os.path
from typing import Any
from uuid import UUID

import pandas as pd

from src.cache.redis_cache import Cache
from src.database import redis
from src.task.config import menu_excel_path


async def check_discount() -> dict[UUID, Any] | dict:
    """Function for parsing Excel file,
    getting dishes discounts and return them.
    """
    discounts = dict()
    if os.path.isfile(menu_excel_path):
        data = pd.read_excel(menu_excel_path, header=None)
        for _, row in data.iterrows():
            row_data = row.values
            if len(row_data) == 7:
                if (not pd.isnull(row_data[2])) and (pd.isnull(row_data[0]) and pd.isnull(row_data[1])):
                    if not pd.isnull(row_data[6]):
                        discounts[UUID(row_data[2])] = round(row_data[6] / 100, 2)
                    else:
                        discounts[UUID(row_data[2])] = None
    return discounts


async def different_between_discounts(excel_data_list: list[Any]) -> str:
    """Function for comparing discounts between
    current Excel data and Excel data in cache.
    If they different then updating cache.

    excel_data_list:
    """
    async with redis as client:
        cache = Cache()
        cache_data = await cache.get(client, 'excel')

    if (cache_data is None) or (excel_data_list != cache_data):
        async with redis as client:
            cache = Cache()
            await cache.add(client, 'excel', excel_data_list)
            for item in excel_data_list:
                await cache.excel_cascade_delete(client, item[0])
            return 'Discount changes detected'
    return 'No changes found'
