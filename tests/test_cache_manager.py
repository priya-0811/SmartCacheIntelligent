import pytest
from backend.cache.ram_cache import RAMCacheManager

def test_cache_manager_put_get():
    cache = RAMCacheManager(max_size_mb=10.0, eviction_policy="hybrid")
    
    test_path = "/tmp/test_file.txt"
    test_data = b"Hello SmartCache In-Memory World!"
    
    # Cache Put
    cache.put(test_path, test_data)
    assert cache.get_current_bytes() == len(test_data)
    
    # Cache Get Hit
    hit_res = cache.get(test_path)
    assert hit_res is not None
    bytes_retrieved, latency_ms = hit_res
    assert bytes_retrieved == test_data
    assert latency_ms >= 0.0
    
    # Cache Miss
    miss_res = cache.get("/tmp/non_existent.txt")
    assert miss_res is None
    
    # Verify Stats
    stats = cache.get_stats()
    assert stats["hit_count"] == 1
    assert stats["miss_count"] == 1
    assert stats["cached_files_count"] == 1

def test_cache_manager_clear():
    cache = RAMCacheManager(max_size_mb=5.0)
    cache.put("/tmp/file1.bin", b"Data 1")
    cache.put("/tmp/file2.bin", b"Data 2")
    
    assert cache.get_current_bytes() > 0
    cache.clear()
    assert cache.get_current_bytes() == 0
    assert cache.get("/tmp/file1.bin") is None

def test_cache_manager_capacity_eviction():
    # Set tiny capacity limit of 100 bytes
    cache = RAMCacheManager(max_size_mb=0.0001, eviction_policy="lru")
    
    file1 = "/tmp/f1.txt"
    file2 = "/tmp/f2.txt"
    
    payload1 = b"A" * 60
    payload2 = b"B" * 60
    
    cache.put(file1, payload1)
    # Adding payload2 should trigger eviction of file1
    cache.put(file2, payload2)
    
    assert cache.get(file1) is None  # Evicted
    assert cache.get(file2) is not None
    assert cache.eviction_count >= 1
