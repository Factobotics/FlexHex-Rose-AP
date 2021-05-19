import aioredis
import logging
import traceback

from aioredis.commands import Redis

logger = logging.getLogger("redis")

class RedisDB:
    def __init__(self,
        host="127.0.0.1",
        port=6379,
        db=0,
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
        self.host=host
        self.port=port
        self.db=db
        self.password=password
        self.ssl=ssl
        self.encoding=encoding
        self.commands_factory=commands_factory
        self.minsize=minsize
        self.maxsize=maxsize
        self.parser=parser
        self.timeout=timeout
        self.pool_cls=pool_cls
        self.connection_cls=connection_cls
        self.loop=loop
        self.redis = None

    async def get_connection(self):
        try:
            self.redis = await aioredis.create_redis_pool(
                (self.host, self.port), db=self.db,
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
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())


    async def set_key(self, key, value):
        if self.redis == None:
            await self.get_connection()
        if self.redis != None:
            await self.redis.set(key, value)
            return True
        else:
            return False


    async def get_key(self, key):
        if self.redis == None:
            await self.get_connection()
        if self.redis != None:
            return await self.redis.get(key, encoding='utf-8')
        else:
            return False


    async def close_connection(self):
        if self.redis != None:
            self.redis.close()
            await self.redis.wait_closed()
        return True