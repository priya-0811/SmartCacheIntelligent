import time
from backend.cache.cache_entry import CacheEntry
from backend.eviction.lru import LRUEvictionPolicy
from backend.eviction.lfu import LFUEvictionPolicy
from backend.eviction.hybrid import HybridEvictionPolicy

def test_lru_eviction_policy():
    policy = LRUEvictionPolicy()
    
    entries = {
        "/path/a.txt": CacheEntry(filepath="/path/a.txt", filesize=10, binary_bytes=b"a", last_accessed_timestamp=100.0),
        "/path/b.txt": CacheEntry(filepath="/path/b.txt", filesize=10, binary_bytes=b"b", last_accessed_timestamp=50.0),  # Oldest
        "/path/c.txt": CacheEntry(filepath="/path/c.txt", filesize=10, binary_bytes=b"c", last_accessed_timestamp=200.0)
    }
    
    victim = policy.select_victim(entries)
    assert victim == "/path/b.txt"

def test_lfu_eviction_policy():
    policy = LFUEvictionPolicy()
    
    entries = {
        "/path/a.txt": CacheEntry(filepath="/path/a.txt", filesize=10, binary_bytes=b"a", access_frequency=10),
        "/path/b.txt": CacheEntry(filepath="/path/b.txt", filesize=10, binary_bytes=b"b", access_frequency=2),  # Lowest frequency
        "/path/c.txt": CacheEntry(filepath="/path/c.txt", filesize=10, binary_bytes=b"c", access_frequency=5)
    }
    
    victim = policy.select_victim(entries)
    assert victim == "/path/b.txt"

def test_hybrid_eviction_policy():
    policy = HybridEvictionPolicy()
    
    entries = {
        "/path/a.txt": CacheEntry(filepath="/path/a.txt", filesize=10, binary_bytes=b"a", access_frequency=10, last_accessed_timestamp=time.time()),
        "/path/b.txt": CacheEntry(filepath="/path/b.txt", filesize=10, binary_bytes=b"b", access_frequency=1, last_accessed_timestamp=time.time() - 3600.0)  # Low freq & old
    }
    
    victim = policy.select_victim(entries)
    assert victim == "/path/b.txt"
