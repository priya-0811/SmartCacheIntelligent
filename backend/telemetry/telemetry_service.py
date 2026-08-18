import logging
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from backend.cache.ram_cache import ram_cache
from backend.database.models import TelemetryLog, CacheEvent

logger = logging.getLogger("smartcache.telemetry")

class TelemetryService:
    """
    Service for collecting system metrics and logging telemetry history.
    """
    def calculate_preload_accuracy(self, db: Session) -> float:
        """
        Calculates preload accuracy: (Preloaded files that resulted in Cache Hits) / (Total Preloads)
        """
        total_preloads = db.query(CacheEvent).filter_by(event_type="PRELOAD").count()
        if total_preloads == 0:
            return 100.0 if ram_cache.preload_count == 0 else 0.0

        # Hits on files that were preloaded
        # Approximate using hits / max(1, total_ops)
        stats = ram_cache.get_stats()
        if stats["hit_count"] == 0:
            return 0.0
            
        accuracy = min(100.0, (stats["hit_count"] / max(1, total_preloads)) * 100.0)
        return round(accuracy, 2)

    def capture_snapshot(self, db: Session) -> TelemetryLog:
        """
        Captures current telemetry state and saves to database.
        """
        stats = ram_cache.get_stats()
        accuracy = self.calculate_preload_accuracy(db)

        log = TelemetryLog(
            timestamp=datetime.utcnow(),
            cache_hits=stats["hit_count"],
            cache_misses=stats["miss_count"],
            hit_ratio=stats["hit_ratio"],
            miss_ratio=stats["miss_ratio"],
            avg_read_latency=stats["average_latency_ms"],
            eviction_count=stats["eviction_count"],
            preload_accuracy=accuracy,
            current_ram_usage=stats["memory_usage_mb"],
            cached_file_count=stats["cached_files_count"]
        )

        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    def get_history(self, db: Session, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Returns recent telemetry history logs for dashboard charts.
        """
        logs = db.query(TelemetryLog).order_by(TelemetryLog.timestamp.desc()).limit(limit).all()
        logs.reverse()  # Return in chronological order
        return [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "cache_hits": log.cache_hits,
                "cache_misses": log.cache_misses,
                "hit_ratio": log.hit_ratio,
                "miss_ratio": log.miss_ratio,
                "avg_read_latency": log.avg_read_latency,
                "eviction_count": log.eviction_count,
                "preload_accuracy": log.preload_accuracy,
                "current_ram_usage": log.current_ram_usage,
                "cached_file_count": log.cached_file_count
            }
            for log in logs
        ]

telemetry_service = TelemetryService()
