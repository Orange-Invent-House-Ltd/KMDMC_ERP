import json
import os

import redis
from django.conf import settings

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")


class Cache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cache, cls).__new__(cls)
            msg = f"REDIS-{ENVIRONMENT.upper()} INSTANTIATED SUCCESSFULLY"
            print("===================================================")
            print(msg)
            print("===================================================")
            cls._instance._redis = redis.Redis(
                host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0
            )
        return cls._instance

    def set(self, key, value, ttl=3600):
        value = json.dumps(value)
        self._redis.set(key, value, ex=ttl)

    def get(self, key):
        data = self._redis.get(key)
        return json.loads(data) if data else None

    def delete(self, key):
        self._redis.delete(key)

    def flush(self):
        self._redis.flushdb()

    def expiry_time(self, key):
        return self._redis.ttl(key)

    def set_expiry(self, key, ttl):
        self._redis.expire(key, ttl)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._redis.connection_pool.disconnect()

    def __del__(self):
        self._redis.connection_pool.disconnect()
