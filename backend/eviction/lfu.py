from typing import Dict, Any, Optional
from backend.eviction.base import BaseEvictionPolicy

class LFUEvictionPolicy(BaseEvictionPolicy):
    """
    Least Frequently Used (LFU) Eviction Policy.
    Evicts the file with the lowest access_frequency count.
    """
    def select_victim(self, cache_entries: Dict[str, Any]) -> Optional[str]:
        if not cache_entries:
            return None
        
        victim_key = None
        min_frequency = float('inf')
        
        for key, entry in cache_entries.items():
            freq = entry.access_frequency
            if freq < min_frequency:
                min_frequency = freq
                victim_key = key
            elif freq == min_frequency:
                # Tie-breaker: choose the older access timestamp
                if entry.last_accessed_timestamp < cache_entries[victim_key].last_accessed_timestamp:
                    victim_key = key
                    
        return victim_key
