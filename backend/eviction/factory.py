from typing import Dict, Any, Optional
from backend.eviction.base import BaseEvictionPolicy
from backend.eviction.lru import LRUEvictionPolicy
from backend.eviction.lfu import LFUEvictionPolicy
from backend.eviction.hybrid import HybridEvictionPolicy

class EvictionEngine:
    """
    Factory & Manager for Eviction Policies.
    Supports LRU, LFU, and Hybrid eviction policies with dynamic switching.
    """
    def __init__(self, policy_name: str = "hybrid"):
        self._policies: Dict[str, BaseEvictionPolicy] = {
            "lru": LRUEvictionPolicy(),
            "lfu": LFUEvictionPolicy(),
            "hybrid": HybridEvictionPolicy()
        }
        self._current_policy_name = policy_name.lower()

    @property
    def current_policy(self) -> str:
        return self._current_policy_name

    def set_policy(self, policy_name: str) -> bool:
        policy_name_clean = policy_name.lower()
        if policy_name_clean in self._policies:
            self._current_policy_name = policy_name_clean
            return True
        return False

    def select_victim(self, cache_entries: Dict[str, Any]) -> Optional[str]:
        policy = self._policies.get(self._current_policy_name, self._policies["hybrid"])
        return policy.select_victim(cache_entries)
