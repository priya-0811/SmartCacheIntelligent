import time
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class CacheEntry:
    filepath: str
    filesize: int
    binary_bytes: bytes
    cached_timestamp: float = field(default_factory=time.time)
    last_accessed_timestamp: float = field(default_factory=time.time)
    access_frequency: int = 1
    hit_count: int = 0
    miss_count: int = 1  # Loaded on a miss

    def touch(self):
        """Update access timestamp and access frequency on cache hit."""
        self.last_accessed_timestamp = time.time()
        self.access_frequency += 1
        self.hit_count += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filepath": self.filepath,
            "filesize": self.filesize,
            "cached_timestamp": self.cached_timestamp,
            "last_accessed_timestamp": self.last_accessed_timestamp,
            "access_frequency": self.access_frequency,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count
        }
