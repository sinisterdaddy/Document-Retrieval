from fastapi import APIRouter, Depends, HTTPException
from elasticsearch import Elasticsearch
from app.caching import get_redis_cache
from app.models import get_user, update_user_requests
import time

router = APIRouter()

es = Elasticsearch()
cache = get_redis_cache()

@router.get("/search")
def search_documents(text: str, top_k: int = 10, threshold: float = 0.5, user_id: str):
    # Rate limiting
    user = get_user(user_id)
    if user and user.requests_count >= 5:
        raise HTTPException(status_code=429, detail="Too many requests")

    start_time = time.time()

    # Search query
    query = {
        "query": {
            "match": {
                "content": text
            }
        },
        "size": top_k
    }
    
    # Caching logic
    cache_key = f"{user_id}:{text}:{top_k}:{threshold}"
    if cache.exists(cache_key):
        results = cache.get(cache_key)
    else:
        results = es.search(index="documents", body=query)["hits"]["hits"]
        cache.set(cache_key, results)

    # Update user request count
    update_user_requests(user_id)

    # Log inference time
    inference_time = time.time() - start_time

    return {"results": results, "inference_time": inference_time}
