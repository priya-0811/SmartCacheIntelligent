from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.cache.ram_cache import ram_cache
from backend.predictor.markov_predictor import markov_predictor

router = APIRouter(prefix="/cache", tags=["Cache Controller"])

class CacheConfigUpdate(BaseModel):
    max_size_mb: float | None = Field(None, ge=1.0, le=10000.0, description="Max cache capacity in MB")
    eviction_algorithm: str | None = Field(None, description="LRU, LFU, or Hybrid")
    preload_threshold: float | None = Field(None, ge=0.0, le=1.0, description="Markov preloader threshold (e.g. 0.70)")

@router.post("/clear")
def clear_cache():
    """
    Clears all binary contents and metadata from RAM cache.
    """
    ram_cache.clear()
    return {"status": "success", "message": "RAM cache successfully cleared."}

@router.get("/stats")
def get_cache_stats():
    """
    Returns live metrics including Hit ratio, Miss ratio, Memory usage, Cached files, Total bytes, and Average latency.
    """
    return ram_cache.get_stats()

@router.get("/files")
def get_cached_files():
    """
    Returns a list of all files currently stored in RAM cache.
    """
    return {
        "count": len(ram_cache._cache),
        "files": ram_cache.get_all_entries()
    }

@router.post("/config")
def update_cache_config(config: CacheConfigUpdate):
    """
    Dynamically update cache capacity, eviction algorithm, or Markov threshold at runtime.
    """
    updated = {}

    if config.max_size_mb is not None:
        ram_cache.set_max_size_mb(config.max_size_mb)
        updated["max_size_mb"] = config.max_size_mb

    if config.eviction_algorithm is not None:
        success = ram_cache.eviction_engine.set_policy(config.eviction_algorithm)
        if not success:
            raise HTTPException(status_code=400, detail=f"Invalid eviction policy: {config.eviction_algorithm}. Choose from 'lru', 'lfu', 'hybrid'.")
        updated["eviction_algorithm"] = config.eviction_algorithm.lower()

    if config.preload_threshold is not None:
        markov_predictor.set_threshold(config.preload_threshold)
        updated["preload_threshold"] = config.preload_threshold

    return {
        "status": "success",
        "message": "Cache configuration updated successfully.",
        "updated_settings": updated,
        "current_stats": ram_cache.get_stats()
    }
