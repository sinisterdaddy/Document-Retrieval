from fastapi import APIRouter, Depends, HTTPException
from elasticsearch import Elasticsearch
from app.caching import get_redis_cache
from app.models import get_user, update_user_requests
import time
from app.caching import LayeredCache, LRUCache
router = APIRouter()

es = Elasticsearch()
cache = get_redis_cache()

@router.get("/search")
def search_documents(text: str, user_id: str, top_k: int = 10, threshold: float = 0.5):
    # Rate limiting
    user = get_user(user_id)
    if user and user['requests_count'] >= 5:
        raise HTTPException(status_code=429, detail="Too many requests")

    start_time = time.time()

    # Cache key generation
    cache_key = f"{user_id}:{text}:{threshold}"
    
    # Check in LRU Cache first
    lru_cache = LRUCache(capacity=100)
    if lru_cache.exists(cache_key):
        results = lru_cache.get(cache_key)
    else:
        # If not found, check in Redis (or Layered Cache)
        if LayeredCache.exists(cache_key):
            results = LayeredCache.get(cache_key)
        else:
            # Perform search query
            query = {
                "query": {
                    "match": {
                        "content": text
                    }
                },
                "size": top_k
            }
            results = es.search(index="documents", body=query)["hits"]["hits"]
            
            # Store in Redis and LRU Cache
            LayeredCache.set(cache_key, results, ttl=3600)
            lru_cache.set(cache_key, results)

    # Update user request count
    update_user_requests(user_id)

    # Log inference time
    inference_time = time.time() - start_time

    return {"results": results, "inference_time": inference_time}
