import time
from typing import Dict, Any, Optional
from backend.eviction.base import BaseEvictionPolicy

class HybridEvictionPolicy(BaseEvictionPolicy):
    """
    Hybrid Eviction Policy.
    Score = 0.6 * AccessFrequency + 0.4 * RecentAccessWeight
    Evicts the file with the lowest score.
    """
    def select_victim(self, cache_entries: Dict[str, Any]) -> Optional[str]:
        if not cache_entries:
            return None
        
        now = time.time()
        max_freq = max((entry.access_frequency for entry in cache_entries.values()), default=1)
        if max_freq == 0:
            max_freq = 1

        victim_key = None
        min_score = float('inf')

        for key, entry in cache_entries.items():
            # Normalized access frequency [0.0 - 1.0]
            norm_freq = entry.access_frequency / max_freq

            # Recency weight decay: 1.0 when accessed right now, decays over time
            elapsed_seconds = max(0.0, now - entry.last_accessed_timestamp)
            recent_weight = 1.0 / (1.0 + (elapsed_seconds / 60.0))  # 60s half-life scale factor

            score = 0.6 * norm_freq + 0.4 * recent_weight

            if score < min_score:
                min_score = score
                victim_key = key

        return victim_key
