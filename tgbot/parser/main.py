import asyncio
import logging
import random
from typing import Any, List

from parser.category import Category
from parser.wb_parser import WBParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_specific_product_for_category(shard: str, query: str,
                                            filters: list = None) -> list[
    dict]:
    pass


async def main_parsing() -> list[Any]:
    """
    Main parsing function that fetches single products from each leaf category.

    Returns:
        List[dict]: A list of parsed product dictionaries.
    """
    flat_list = None
    return flat_list


if __name__ == "__main__":
    asyncio.run(main_parsing())
