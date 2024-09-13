from redis import Redis

# Assume we're storing users in Redis for simplicity
redis_client = Redis()

def get_user(user_id: str):
    return redis_client.hgetall(f"user:{user_id}")

def update_user_requests(user_id: str):
    user_key = f"user:{user_id}"
    if redis_client.exists(user_key):
        redis_client.hincrby(user_key, "requests_count", 1)
    else:
        redis_client.hmset(user_key, {"requests_count": 1})
