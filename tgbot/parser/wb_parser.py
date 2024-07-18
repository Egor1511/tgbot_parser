import asyncio
import logging
from typing import Dict, Any

import aiohttp
from parser.filter import Filter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WBParser:
    BASE_URL = 'https://catalog.wb.ru/catalog/{shard}/v2/catalog'
    PRODUCT_DETAIL_URL = 'https://card.wb.ru/cards/v2/detail'

    def __init__(self, shard: str, query: str):
        """
        Initializes the WBParser with the given shard and query.

        Args:
            shard (str): The shard identifier for the catalog.
            query (str): The query string for the catalog.
        """
        self.shard = shard
        self.query = query

    def _build_params(self, skip: int, limit: int,
                      filters: dict[str, str] | None = None) -> dict:
        """
        Builds the parameters for the catalog request.

        Args:
            skip (int): Number of items to skip.
            limit (int): Number of items to fetch.
            filters (Optional[Dict[str, str]]): Dictionary
            of filter keys and their values.

        Returns:
            dict: Dictionary of parameters.
        """
        params = {
            'ab_testing': 'false',
            'appType': '1',
            'curr': 'rub',
            'dest': '123586067',
            'sort': 'popular',
            'spp': '30',
            'skip': skip,
            'limit': limit,
        }
        params.update(dict(item.split('=') for item in self.query.split('&')))
        if filters:
            params.update(filters)
        return params

    async def __fetch_data(self, url: str,
                           params: Dict[str, str]) -> Any | None:
        """
        Fetches data from the given URL with specified parameters.

        Args:
            url (str): The URL to fetch data from.
            params (Dict[str, str]): The parameters for the request.

        Returns:
            Optional[Dict[str, Any]]: JSON response as a dictionary or None if an error occurs.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error occurred: {e}")
        except ValueError as e:
            logger.error(f"JSON decode error: {e}")
        return None

    async def get_products(self, skip: int, limit: int,
                           filters: dict[str, str] = None) -> dict[
                                                                  str, Any] | None:
        """
        Fetches products from the catalog.

        Args:
            skip (int): Number of items to skip.
            limit (int): Number of items to fetch.
            filters (Optional[Dict[str, str]]): Dictionary of filter keys and their values.

        Returns:
            Optional[Dict[str, Any]]: JSON response as a dictionary or None if an error occurs.
        """
        params = self._build_params(skip, limit, filters)
        return await self.__fetch_data(self.BASE_URL.format(shard=self.shard),
                                       params)

    async def get_product_details(self, product_id: str) -> dict[
                                                                str, Any] | None:
        """
        Fetches product details from the catalog.

        Args:
            product_id (str): ID of the product.

        Returns:
            Optional[Dict[str, Any]]: JSON response as a dictionary or None if an error occurs.
        """
        params = {
            'appType': '1',
            'curr': 'rub',
            'dest': '-5854091',
            'spp': '30',
            'ab_testing': 'false',
            'nm': product_id
        }
        return await self.__fetch_data(self.PRODUCT_DETAIL_URL, params)

    async def _get_filter_params(self, filters: list[tuple[
        str, str]] | None = None) -> dict[str, str] | None:
        """
        Get the filter parameters for a list of filters.

        Args:
            filters (Optional[List[Tuple[str, str]]]): A list
            of tuples containing filter names and filter value names.

        Returns:
            Optional[Dict[str, str]]: A dictionary of filter keys
            and their corresponding values if found, otherwise None.
        """
        if not filters:
            return None

        filter_instance = Filter(self.shard, self.query)
        filter_params = {}
        for filter_name, filter_value_name in filters:
            filter_key, filter_id = await filter_instance.get_filter_params(
                filter_name, filter_value_name)
            if not filter_key or not filter_id:
                logger.error(
                    f"Filter '{filter_name}' with value '{filter_value_name}' not found, aborting.")
                return None
            filter_params[filter_key] = filter_id
        return filter_params

    async def _fetch_all_products(self, filters: dict[str, str] | None,
                                  limit: int, max_count: int) -> list[dict]:
        """
        Fetch all products that match the given filter parameters.

        Args:
            filters (Optional[Dict[str, str]]): Dictionary of filter keys
            and their values.
            limit (int): Number of items to fetch per request.
            max_count (int): Maximum number of items to fetch.

        Returns:
            List[dict]: A list of all products.
        """
        all_products = []
        skip = 0

        products_data = await self.get_products(skip, limit, filters)
        if not products_data:
            logger.error("No products data received.")
            return all_products

        total_count = products_data.get('data', {}).get('total', 0)
        if total_count == 0:
            logger.info("No products found in total.")
            return all_products

        products = products_data.get('data', {}).get('products', [])
        all_products.extend(products)

        tasks = []
        for skip in range(limit, min(total_count, max_count), limit):
            tasks.append(self.get_products(skip, limit, filters))

        results = await asyncio.gather(*tasks)
        for result in results:
            if result:
                products = result.get('data', {}).get('products', [])
                all_products.extend(products)
                if len(all_products) >= max_count:
                    break

        return all_products[:max_count]

    def _extract_relevant_fields(self, product: dict) -> bool | dict[
        str, str | float | int | Any]:
        """
        Extracts relevant fields from the product dictionary.

        Args:
            product (dict): The original product dictionary.

        Returns:
            dict: A dictionary with the relevant fields.
        """
        if product['totalQuantity'] == 0:
            return False
        basic_price = product['sizes'][0]['price']['basic']
        total_price = product['sizes'][0]['price']['total']
        discount = round((basic_price - total_price) / basic_price * 100)
        product_id = product['id']
        return {
            'name': product['name'],
            'brand': product['brand'],
            'id': product_id,
            'totalQuantity': product['totalQuantity'],
            'reviewRating': product['reviewRating'],
            'price': total_price / 100,
            'discount': discount,
            'url': self.__get_card_url(product_id),
            'image': self.__get_product_image(product_id),
        }

    def __get_card_url(self, product_id: str) -> str:
        """
        Builds the URL for the product card.

        Args:
            product_id (str): The product ID.

        Returns:
            str: The URL for the product card.
        """
        base_card_url = "https://www.wildberries.ru/catalog/{}/detail.aspx"
        return base_card_url.format(product_id)

    def __get_product_image(self, product_id: int) -> str:
        """
        Builds the URL for the product image.

        Args:
            product_id (str): The product ID.
            root_id (str): The root ID of the product.

        Returns:
            str: The URL for the product image.
        """
        product_id_str = str(product_id)
        k = len(product_id_str) - 5
        e = int(product_id[:k])
        match e:
            case e if e <= 143:
                t = "01"
            case e if e <= 287:
                t = "02"
            case e if e <= 431:
                t = "03"
            case e if e <= 719:
                t = "04"
            case e if e <= 1007:
                t = "05"
            case e if e <= 1061:
                t = "06"
            case e if e <= 1115:
                t = "07"
            case e if e <= 1169:
                t = "08"
            case e if e <= 1313:
                t = "09"
            case e if e <= 1601:
                t = "10"
            case e if e <= 1655:
                t = "11"
            case e if e <= 1919:
                t = "12"
            case e if e <= 2045:
                t = "13"
            case e if e <= 2189:
                t = "14"
            case e if e <= 2405:
                t = "15"
            case e if e <= 2621:
                t = "16"
            case _:
                t = "17"

        basket_host = f"basket-{t}.wbbasket.ru"
        base_image_url = "https://{}/vol{}/part{}/{}/images/big/1.webp"
        return base_image_url.format(basket_host, product_id[:k],
                                     product_id[:k + 2], product_id)

    async def parse_all_products(self,
                                 filters: list[tuple[str, str]] | None = None,
                                 limit: int = 100, max_count: int = 1000) -> \
            list[dict]:
        """
        Parse all products that match the given filters.

        Args:
            filters (Optional[List[Tuple[str, str]]]): A list of tuples
            containing filter names and filter value names.
            limit (int): Number of items to fetch per request (default is 100).
            max_count (int): Maximum number of items to fetch (default is 1000).

        Returns:
            List[dict]: A list of all products that match the given filters.
        """
        filter_params = await self._get_filter_params(filters)
        products = await self._fetch_all_products(filter_params, limit,
                                                  max_count)
        return [self._extract_relevant_fields(product) for product in products]
