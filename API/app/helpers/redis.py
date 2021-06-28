import logging
import traceback
import aioredis
from aioredis.commands import Redis

logger = logging.getLogger("redis")


class RedisDB:
    def __init__(self,
                 host="127.0.0.1",
                 port=6379,
                 database=0,
                 password=None,
                 ssl=None,
                 encoding=None,
                 commands_factory=Redis,
                 minsize=1,
                 maxsize=10,
                 parser=None,
                 timeout=None,
                 pool_cls=None,
                 connection_cls=None,
                 loop=None
                 ):
        self.host = host
        self.port = port
        self.database = database
        self.password = password
        self.ssl = ssl
        self.encoding = encoding
        self.commands_factory = commands_factory
        self.minsize = minsize
        self.maxsize = maxsize
        self.parser = parser
        self.timeout = timeout
        self.pool_cls = pool_cls
        self.connection_cls = connection_cls
        self.loop = loop
        self.redis = None

    async def get_connection(self):
        try:
            self.redis = await aioredis.create_redis_pool(
                (self.host, self.port), db=self.database,
                password=self.password,
                ssl=self.ssl,
                encoding=self.encoding,
                commands_factory=self.commands_factory,
                minsize=self.minsize,
                maxsize=self.maxsize,
                parser=self.parser,
                timeout=self.timeout,
                pool_cls=self.pool_cls,
                connection_cls=self.connection_cls,
                loop=self.loop
            )
            return True
        except Exception as error:
            logger.error(error)
            logger.error(traceback.format_exc())
            return False

    async def set_key(self, key, value):
        if self.redis is None:
            await self.get_connection()
        if self.redis is not None:
            await self.redis.set(key, value)
            return True
        return False

    async def get_key(self, key):
        if self.redis is None:
            await self.get_connection()
        if self.redis is not None:
            return await self.redis.get(key, encoding='utf-8')
        return False

    async def delete_key(self, key):
        if self.redis is None:
            await self.get_connection()
        if self.redis is not None:
            return await self.redis.delete(key)
        return False

    async def close_connection(self):
        if self.redis is not None:
            self.redis.close()
            await self.redis.wait_closed()
        return True

    async def check_connection(self):
        if self.redis is not None:
            return self.redis.closed
        return True
