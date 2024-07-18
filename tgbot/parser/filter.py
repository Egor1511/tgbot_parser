import logging
from typing import Any

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Filter:
    BASE_URL = 'https://catalog.wb.ru/catalog/{shard}/v4/filters'

    def __init__(self, shard: str, query: str):
        self.shard = shard
        self.query = query

    async def get_filter_params(self, filter_name: str,
                                filter_value_name: str) -> tuple[None, None] | \
                                                           tuple[Any, Any]:
        """
        Get the filter parameters for a given filter name and filter value name.
        Args:
            filter_name (str): The name of the filter.
            filter_value_name (str): The name of the filter value.
        Returns:
            Optional[Tuple[str, str]]: A tuple containing the filter key
            and filter value ID if found,
            otherwise None.
        """
        params = self._build_params()
        filters = await self.fetch_filters(params)
        if filters is None:
            return None, None

        return self._find_filter(filters, filter_name, filter_value_name)

    def _build_params(self):
        return {
            'ab_testing': 'false',
            'appType': '1',
            'cat': self.query.split('=')[1],
            'curr': 'rub',
            'dest': '-5854091',
            'spp': '30'
        }

    async def fetch_filters(self, params: dict[str, str]) -> dict[
                                                                 str, Any] | None:
        """
        Fetches filters using the provided parameters.
        Args:
            params (Dict[str, str]): The parameters to be used in the request.
        Returns:
            Optional[Dict[str, Any]]: A dictionary containing
            the fetched filters
            if successful,
            otherwise None.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL.format(shard=self.shard),
                                       params=params) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error occurred: {e}")
        except ValueError as e:
            logger.error(f"JSON decode error: {e}")
        return None

    def _find_filter(
            self,
            filters: dict[str, Any],
            filter_name: str,
            filter_value_name: str
    ) -> tuple[Any, Any] | tuple[None, None]:
        """
        Finds a filter key and value ID based on the given filters,
        filter name, and filter value name.
        Args:
            filters (Dict[str, Any]): The filters dictionary.
            filter_name (str): The name of the filter.
            filter_value_name (str): The name of the filter value.
        Returns:
            Optional[Tuple[str, str]]: A tuple containing
            the filter key and filter value ID if found,
                                       otherwise None.
        """
        for filterer in filters.get('data', {}).get('filters', []):
            if filterer['name'] == filter_name:
                filter_key = filterer['key']
                for value in filterer.get('items', []):
                    if value['name'] == filter_value_name:
                        return filter_key, value['id']
        return None, None
