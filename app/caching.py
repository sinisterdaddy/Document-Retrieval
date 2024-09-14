import redis

def get_redis_cache():
    return redis.Redis(host='localhost', port=6379, db=0)

# You can implement additional caching strategies here if needed
import os
import redis
import pickle
import hashlib

class LayeredCache:
    def __init__(self, redis_client, cache_dir="/tmp/cache"):
        self.redis_client = redis_client
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _hash_key(self, key):
        return hashlib.sha256(key.encode('utf-8')).hexdigest()

    def set(self, key, value, ttl=None):
        # Store in Redis
        self.redis_client.setex(key, ttl, pickle.dumps(value))
        # Store on disk
        with open(os.path.join(self.cache_dir, self._hash_key(key)), 'wb') as f:
            pickle.dump(value, f)

    def get(self, key):
        # Try to get from Redis
        value = self.redis_client.get(key)
        if value:
            return pickle.loads(value)

        # Fallback to disk cache
        try:
            with open(os.path.join(self.cache_dir, self._hash_key(key)), 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None

    def exists(self, key):
        # Check if key exists in Redis or disk cache
        return self.redis_client.exists(key) or os.path.exists(os.path.join(self.cache_dir, self._hash_key(key)))

    def invalidate(self, key):
        # Remove from both Redis and disk cache
        self.redis_client.delete(key)
        disk_cache_path = os.path.join(self.cache_dir, self._hash_key(key))
        if os.path.exists(disk_cache_path):
            os.remove(disk_cache_path)
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: str):
        if key not in self.cache:
            return None
        # Move the accessed item to the end to show that it was recently used
        self.cache.move_to_end(key)
        return self.cache[key]

    def set(self, key: str, value):
        if key in self.cache:
            # Move the accessed item to the end
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # Remove the first item (least recently used)
            self.cache.popitem(last=False)

    def exists(self, key: str):
        return key in self.cache
def set_with_ttl(self, key, value, ttl):
    self.redis_client.setex(key, ttl, pickle.dumps(value))

def get(self, key):
    value = self.redis_client.get(key)
    return pickle.loads(value) if value else None
def get_partial_cache(redis_client, key, top_k):
    partial_key = f"{key}:top_{top_k}"
    return redis_client.get(partial_key)

def set_partial_cache(redis_client, key, top_k, results, ttl):
    partial_key = f"{key}:top_{top_k}"
    redis_client.setex(partial_key, ttl, pickle.dumps(results))
