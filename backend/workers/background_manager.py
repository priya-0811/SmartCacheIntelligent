import os
import time
import queue
import threading
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database.database import SessionLocal
from backend.database.models import CacheEvent, FileMetadata
from backend.cache.ram_cache import ram_cache
from backend.telemetry.telemetry_service import telemetry_service
from backend.cache.file_watcher import WatchdogObserver
from backend.config import settings

logger = logging.getLogger("smartcache.workers")

# Preload work queue for Thread 2
preload_queue: queue.Queue[str] = queue.Queue()

class BackgroundWorkerManager:
    """
    Manages background multithreaded workers for:
    - Thread 1: Telemetry updater
    - Thread 2: Predictive preloader
    - Thread 3: Periodic cleanup
    - Watchdog: File system observer
    """
    def __init__(self):
        self._running = False
        self.thread_telemetry: threading.Thread | None = None
        self.thread_preloader: threading.Thread | None = None
        self.thread_cleanup: threading.Thread | None = None
        self.watchdog_observer = WatchdogObserver(settings.WATCH_DIR)

    def start_all(self):
        if self._running:
            return
        self._running = True
        logger.info("Starting SmartCache Background Workers...")

        # Thread 1: Telemetry updater
        self.thread_telemetry = threading.Thread(
            target=self._run_telemetry_updater,
            name="TelemetryUpdaterWorker",
            daemon=True
        )
        self.thread_telemetry.start()

        # Thread 2: Predictive preloader
        self.thread_preloader = threading.Thread(
            target=self._run_predictive_preloader,
            name="PredictivePreloaderWorker",
            daemon=True
        )
        self.thread_preloader.start()

        # Thread 3: Periodic cleanup
        self.thread_cleanup = threading.Thread(
            target=self._run_periodic_cleanup,
            name="PeriodicCleanupWorker",
            daemon=True
        )
        self.thread_cleanup.start()

        # Watchdog observer for file invalidation
        try:
            self.watchdog_observer.start()
        except Exception as e:
            logger.warning(f"Could not start watchdog observer: {e}")

    def stop_all(self):
        self._running = False
        try:
            self.watchdog_observer.stop()
        except Exception as e:
            logger.warning(f"Error stopping watchdog: {e}")
        logger.info("Background workers stopped.")

    def _run_telemetry_updater(self):
        """Thread 1: Periodically captures and stores telemetry metrics."""
        while self._running:
            try:
                db: Session = SessionLocal()
                try:
                    telemetry_service.capture_snapshot(db)
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"Error in TelemetryUpdaterWorker: {e}")
            time.sleep(5)  # Collect every 5 seconds

    def _run_predictive_preloader(self):
        """Thread 2: Processes preloading tasks asynchronously without blocking requests."""
        while self._running:
            try:
                try:
                    filepath = preload_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                abs_path = os.path.abspath(filepath)
                
                # Check if already cached
                if abs_path in ram_cache._cache:
                    preload_queue.task_done()
                    continue

                if not os.path.exists(abs_path):
                    logger.warning(f"Preload target file not found: {abs_path}")
                    preload_queue.task_done()
                    continue

                # Read from disk in background thread
                start_t = time.perf_counter()
                with open(abs_path, "rb") as f:
                    content = f.read()

                # Put into RAM Cache
                ram_cache.put(abs_path, content, is_preload=True)
                read_latency = (time.perf_counter() - start_t) * 1000.0

                # Log PRELOAD event in DB
                db: Session = SessionLocal()
                try:
                    file_meta = db.query(FileMetadata).filter_by(filepath=abs_path).first()
                    file_id = file_meta.id if file_meta else None
                    
                    event = CacheEvent(
                        file_id=file_id,
                        event_type="PRELOAD",
                        timestamp=datetime.utcnow()
                    )
                    db.add(event)
                    db.commit()
                    logger.info(f"Successfully preloaded file into RAM cache: {abs_path} (Latency: {read_latency:.2f}ms)")
                finally:
                    db.close()

                preload_queue.task_done()
            except Exception as e:
                logger.error(f"Error in PredictivePreloaderWorker: {e}")

    def _run_periodic_cleanup(self):
        """Thread 3: Performs periodic system cleanup and stale log purging."""
        while self._running:
            try:
                # Run cleanup every 60 seconds
                time.sleep(60)
                if not self._running:
                    break

                db: Session = SessionLocal()
                try:
                    # Clean up cache events older than 7 days if any
                    cutoff = datetime.utcnow() - timedelta(days=7)
                    deleted = db.query(CacheEvent).filter(CacheEvent.timestamp < cutoff).delete()
                    db.commit()
                    if deleted > 0:
                        logger.info(f"Periodic cleanup purged {deleted} old cache events.")
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"Error in PeriodicCleanupWorker: {e}")

# Global background worker manager
worker_manager = BackgroundWorkerManager()
