import logging
from typing import Any

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Category:
    BASE_URL = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v2.json'

    def __init__(self, category_name: str = None):
        """
        Initializes the Category with the given category name.

        Args:
            category_name (str): The name of the category to search for.
        """
        self.category_name = category_name

    async def fetch_data(self) -> dict | None:
        """
        Fetches data from the specified URL and returns it as a dictionary.

        Returns:
            dict | None: The fetched data or None if an error occurs.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error occurred: {e}")
        except ValueError as e:
            logger.error(f"JSON decode error: {e}")
        return None

    async def get_all_leaf_categories(self) -> list[tuple[str, str]]:
        """
        Retrieves all leaf categories (categories without child categories)
        with their 'shard' and 'query'.

        Returns:
            list[tuple[str, str]]: A list of tuples containing 'shard'
            and 'query' for each leaf category.
        """
        data = await self.fetch_data()
        if data is None:
            return []
        return await self._find_all_leaf_categories(data)

    async def _find_all_leaf_categories(self, data: list[dict[str, Any]]) -> \
    list[tuple[str, str]]:
        """
        Recursively searches for all leaf categories in the given data.

        Args:
            data (list[dict[str, Any]]): The data to search in.

        Returns:
            list[tuple[str, str]]: A list of tuples containing 'shard'
            and 'query' for each leaf category.
        """
        leaf_categories = []
        for category in data:
            if 'childs' in category:
                leaf_categories.extend(
                    await self._find_all_leaf_categories(category['childs']))
            elif 'shard' in category and 'query' in category:
                leaf_categories.append((category['shard'], category['query']))
        return leaf_categories

    async def get_categories_by_names(self, names: list[str]) -> list[
        dict[str, Any]]:
        """
        Retrieves the categories with the specified names.

        Args:
            names (list[str]): The list of category names to search for.

        Returns:
            list[dict[str, Any]]: A list of dictionaries representing
            the found categories.
        """
        data = await self.fetch_data()
        if data is None:
            return []
        return await self._find_categories_by_names(data, names)

    async def _find_categories_by_names(self, data: list[dict[str, Any]],
                                        names: list[str]) -> list[
        dict[str, Any]]:
        """
        Recursively searches for categories with the specified names
        in the given data.

        Args:
            data (list[dict[str, Any]]): The data to search in.
            names (list[str]): The list of category names to search for.

        Returns:
            list[dict[str, Any]]: A list of dictionaries representing
            the found categories.
        """
        found_categories = []
        for category in data:
            if category['name'] in names:
                found_categories.append(category)
            if 'childs' in category:
                found_categories.extend(
                    await self._find_categories_by_names(category['childs'],
                                                         names))
        return found_categories
