import json
import redis.asyncio as redis


class RedisDB:
    def __init__(self, host: str, port: int, db: int):
        """
        Initializes the RedisDB instance.

        Args:
            host (str): The Redis server host.
            port (int): The Redis server port.
            db (int): The Redis database number.
        """
        self.host = host
        self.port = port
        self.db = db
        self.r = self.__create_db()

    def __create_db(self) -> redis.Redis:
        """
        Creates the Redis client instance.

        Returns:
            redis.Redis: The Redis client.
        """
        return redis.Redis(host=self.host, port=self.port, db=self.db)

    async def __modify_stack(self, stack_name: str, action: str, product: dict = None, products: list[dict] = None):
        """
        Helper function to perform actions on stack.

        Args:
            stack_name (str): The name of the stack.
            action (str): Action to perform ('lpush', 'rpush', 'delete', 'lpop', 'lrange').
            product (dict, optional): Product for 'lpush' or 'rpush' actions.
            products (list[dict], optional): List of products for 'lpush' action.
        """
        if action == 'delete':
            await self.r.delete(stack_name)
        elif action == 'lpush' and products is not None:
            await self.r.lpush(stack_name, *[json.dumps(product) for product in products])
        elif action in ['lpush', 'rpush'] and product is not None:
            await getattr(self.r, action)(stack_name, json.dumps(product))
        elif action == 'lpop':
            return await self.r.lpop(stack_name)
        elif action == 'lrange':
            return await self.r.lrange(stack_name, 0, -1)

    async def create_stack(self, products: list[dict], stack_name: str):
        """
        Creates a stack of products in Redis.

        Args:
            products (list[dict]): The list of products to add to the stack.
            stack_name (str): The name of the stack.
        """
        await self.__modify_stack(stack_name, 'delete')
        await self.__modify_stack(stack_name, 'lpush', products=products)

    async def delete_stack(self, stack_name: str):
        """
        Deletes a stack from Redis.

        Args:
            stack_name (str): The name of the stack to delete.
        """
        await self.__modify_stack(stack_name, 'delete')

    async def add_product_to_stack(self, product: dict, stack_name: str):
        """
        Adds a product to the start of the stack in Redis.

        Args:
            product (dict): The product to add.
            stack_name (str): The name of the stack.
        """
        await self.__modify_stack(stack_name, 'lpush', product=product)

    async def add_product_to_end_of_stack(self, product: dict, stack_name: str):
        """
        Adds a product to the end of the stack in Redis.

        Args:
            product (dict): The product to add.
            stack_name (str): The name of the stack.
        """
        await self.__modify_stack(stack_name, 'rpush', product=product)

    async def get_all_products(self, stack_name: str) -> list[dict]:
        """
        Retrieves all products from the stack in Redis.

        Args:
            stack_name (str): The name of the stack.

        Returns:
            list[dict]: The list of products.
        """
        products = await self.__modify_stack(stack_name, 'lrange')
        return [json.loads(product) for product in products]

    async def get_and_remove_first_product(self, stack_name: str) -> dict | None:
        """
        Retrieves and removes the first product from the stack in Redis.

        Args:
            stack_name (str): The name of the stack.

        Returns:
            Union[dict, None]: The first product or None if the stack is empty.
        """
        product_json = await self.__modify_stack(stack_name, 'lpop')
        if product_json:
            return json.loads(product_json)
        return None

    async def get_first_product(self, stack_name: str) -> dict | None:
        """
        Retrieves the first product from the stack in Redis.

        Args:
            stack_name (str): The name of the stack.

        Returns:
            Union[dict, None]: The first product or None if the stack is empty.
        """
        product_json = await self.r.lindex(stack_name, 0)
        if product_json:
            return json.loads(product_json)
        return None

    async def delete_first_product(self, stack_name: str):
        """
        Deletes the first product from the stack in Redis.

        Args:
            stack_name (str): The name of the stack.
        """
        await self.__modify_stack(stack_name, 'lpop')

    async def __modify_hash(self, hash_name: str, action: str, key: str = None, value: str = None):
        """
        Helper function to perform actions on hash.

        Args:
            hash_name (str): The name of the hash.
            action (str): Action to perform ('hset', 'hget', 'hdel', 'hexists', 'hkeys').
            key (str, optional): Key for the action.
            value (str, optional): Value for 'hset' action.
        """
        if action == 'hset' and key and value:
            await self.r.hset(hash_name, key, value)
        elif action == 'hget' and key:
            return await self.r.hget(hash_name, key)
        elif action == 'hdel' and key:
            await self.r.hdel(hash_name, key)
        elif action == 'hexists' and key:
            return await self.r.hexists(hash_name, key)
        elif action == 'hkeys':
            return await self.r.hkeys(hash_name)

    async def add_product_user_mapping(self, product_id: str, user_id: str):
        """
        Adds a mapping of product ID to user ID in Redis.

        Args:
            product_id (str): The product ID.
            user_id (str): The user ID.
        """
        await self.__modify_hash('awaits', 'hset', product_id, user_id)

    async def get_user_id_by_product_id(self, product_id: str) -> int | None:
        """
        Retrieves the user ID associated with a product ID from Redis.

        Args:
            product_id (str): The product ID.

        Returns:
            Union[int, None]: The user ID if exists, else None.
        """
        user_id = await self.__modify_hash('awaits', 'hget', product_id)
        if user_id:
            return int(user_id)
        return None

    async def remove_product_user_mapping(self, product_id: str):
        """
        Removes a mapping of product ID to user ID from Redis.

        Args:
            product_id (str): The product ID.
        """
        await self.__modify_hash('awaits', 'hdel', product_id)

    async def hash_key_exists(self, hash_name: str, key: str) -> bool:
        """
        Checks if a key exists in a hash.

        Args:
            hash_name (str): The name of the hash.
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return await self.__modify_hash(hash_name, 'hexists', key)

    async def user_id_exists_in_hash(self, hash_name: str, user_id: str) -> bool:
        """
        Checks if a user_id exists in a hash.

        Args:
            hash_name (str): The name of the hash.
            user_id (str): The user_id to check.

        Returns:
            bool: True if the user_id exists, False otherwise.
        """
        keys = await self.__modify_hash(hash_name, 'hkeys')
        for key in keys:
            if await self.__modify_hash(hash_name, 'hget', key) == user_id.encode('utf-8'):
                return True
        return False
