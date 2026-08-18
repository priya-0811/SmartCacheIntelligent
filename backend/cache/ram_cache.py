import os
import time
import threading
import psutil
from typing import Dict, Optional, List, Tuple, Any
from backend.cache.cache_entry import CacheEntry
from backend.eviction.factory import EvictionEngine
from backend.config import settings

class RAMCacheManager:
    """
    High-performance thread-safe in-memory cache manager.
    Stores binary file contents directly in RAM without using Redis.
    Guarantees that cached data is NEVER written back to disk.
    """
    def __init__(self, max_size_mb: float = settings.MAX_CACHE_SIZE_MB, eviction_policy: str = settings.EVICTION_ALGORITHM):
        self._lock = threading.RLock()
        self._cache: Dict[str, CacheEntry] = {}
        self._max_bytes = int(max_size_mb * 1024 * 1024)
        self.eviction_engine = EvictionEngine(eviction_policy)
        
        # Performance & telemetry metrics counters
        self.total_hits = 0
        self.total_misses = 0
        self.eviction_count = 0
        self.total_read_latency_ms = 0.0
        self.total_read_operations = 0
        self.preload_count = 0

    @property
    def max_size_mb(self) -> float:
        return self._max_bytes / (1024 * 1024)

    def set_max_size_mb(self, new_size_mb: float):
        with self._lock:
            self._max_bytes = int(new_size_mb * 1024 * 1024)
            self._enforce_capacity()

    def get_current_bytes(self) -> int:
        with self._lock:
            return sum(entry.filesize for entry in self._cache.values())

    def get(self, filepath: str) -> Optional[Tuple[bytes, float]]:
        """
        Retrieves file bytes from RAM cache if present.
        Returns (binary_bytes, latency_ms) if HIT, None if MISS.
        """
        start_time = time.perf_counter()
        abs_path = os.path.abspath(filepath)
        
        with self._lock:
            if abs_path in self._cache:
                entry = self._cache[abs_path]
                entry.touch()
                self.total_hits += 1
                
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                self.total_read_latency_ms += latency_ms
                self.total_read_operations += 1
                return entry.binary_bytes, latency_ms
            else:
                self.total_misses += 1
                return None

    def put(self, filepath: str, binary_bytes: bytes, is_preload: bool = False) -> CacheEntry:
        """
        Inserts file bytes into RAM cache. Triggers eviction if capacity is exceeded.
        """
        abs_path = os.path.abspath(filepath)
        filesize = len(binary_bytes)
        
        with self._lock:
            if is_preload:
                self.preload_count += 1
                
            entry = CacheEntry(
                filepath=abs_path,
                filesize=filesize,
                binary_bytes=binary_bytes
            )
            
            self._cache[abs_path] = entry
            self._enforce_capacity()
            return entry

    def _enforce_capacity(self):
        """Evicts entries until total cache size is within max_bytes threshold."""
        while self.get_current_bytes() > self._max_bytes and self._cache:
            victim_key = self.eviction_engine.select_victim(self._cache)
            if not victim_key or victim_key not in self._cache:
                # Fallback to pop arbitrary item if engine returns None
                victim_key = next(iter(self._cache))
                
            del self._cache[victim_key]
            self.eviction_count += 1

    def invalidate(self, filepath: str) -> bool:
        """Invalidates a file entry from cache (e.g., when source file changes)."""
        abs_path = os.path.abspath(filepath)
        with self._lock:
            if abs_path in self._cache:
                del self._cache[abs_path]
                return True
            return False

    def clear(self):
        """Clears all cached RAM entries."""
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total_ops = self.total_hits + self.total_misses
            hit_ratio = (self.total_hits / total_ops) if total_ops > 0 else 0.0
            miss_ratio = (self.total_misses / total_ops) if total_ops > 0 else 0.0
            avg_latency = (self.total_read_latency_ms / self.total_read_operations) if self.total_read_operations > 0 else 0.0
            
            process = psutil.Process()
            memory_info = process.memory_info()
            sys_mem = psutil.virtual_memory()

            return {
                "hit_count": self.total_hits,
                "miss_count": self.total_misses,
                "hit_ratio": round(hit_ratio, 4),
                "miss_ratio": round(miss_ratio, 4),
                "memory_usage_mb": round(self.get_current_bytes() / (1024 * 1024), 2),
                "max_memory_mb": round(self.max_size_mb, 2),
                "memory_utilization_pct": round((self.get_current_bytes() / self._max_bytes) * 100.0, 2) if self._max_bytes > 0 else 0.0,
                "cached_files_count": len(self._cache),
                "total_bytes": self.get_current_bytes(),
                "average_latency_ms": round(avg_latency, 4),
                "eviction_count": self.eviction_count,
                "eviction_algorithm": self.eviction_engine.current_policy,
                "process_ram_mb": round(memory_info.rss / (1024 * 1024), 2),
                "system_ram_utilization_pct": sys_mem.percent
            }

    def get_all_entries(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [entry.to_dict() for entry in self._cache.values()]

# Global singleton RAM cache instance
ram_cache = RAMCacheManager()
