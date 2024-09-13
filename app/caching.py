import redis

def get_redis_cache():
    return redis.Redis(host='localhost', port=6379, db=0)

# You can implement additional caching strategies here if needed
