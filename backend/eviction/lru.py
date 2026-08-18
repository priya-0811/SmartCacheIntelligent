from typing import Dict, Any, Optional
from backend.eviction.base import BaseEvictionPolicy

class LRUEvictionPolicy(BaseEvictionPolicy):
    """
    Least Recently Used (LRU) Eviction Policy.
    Evicts the file with the oldest last_accessed timestamp.
    """
    def select_victim(self, cache_entries: Dict[str, Any]) -> Optional[str]:
        if not cache_entries:
            return None
        
        victim_key = None
        oldest_access = float('inf')
        
        for key, entry in cache_entries.items():
            last_accessed = entry.last_accessed_timestamp
            if last_accessed < oldest_access:
                oldest_access = last_accessed
                victim_key = key
                
        return victim_key
