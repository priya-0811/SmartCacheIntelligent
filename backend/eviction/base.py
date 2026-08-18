from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseEvictionPolicy(ABC):
    @abstractmethod
    def select_victim(self, cache_entries: Dict[str, Any]) -> Optional[str]:
        """
        Given a dictionary of cached entries, return the key (filepath) of the item to evict.
        """
        pass
