import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from backend.cache.ram_cache import ram_cache

logger = logging.getLogger("smartcache.watcher")

class FileWatcherHandler(FileSystemEventHandler):
    """
    Watchdog event handler that invalidates cache entries when source files are modified or deleted.
    """
    def on_modified(self, event):
        if not event.is_directory:
            filepath = os.path.abspath(event.src_path)
            logger.info(f"File modified on disk: {filepath}. Invalidating RAM cache entry.")
            ram_cache.invalidate(filepath)

    def on_deleted(self, event):
        if not event.is_directory:
            filepath = os.path.abspath(event.src_path)
            logger.info(f"File deleted from disk: {filepath}. Removing from RAM cache.")
            ram_cache.invalidate(filepath)

class WatchdogObserver:
    """
    Observer wrapper to manage background directory monitoring.
    """
    def __init__(self, watch_path: str):
        self.watch_path = os.path.abspath(watch_path)
        self.observer = Observer()
        self.event_handler = FileWatcherHandler()

    def start(self):
        if os.path.exists(self.watch_path):
            self.observer.schedule(self.event_handler, path=self.watch_path, recursive=True)
            self.observer.start()
            logger.info(f"Watchdog observer started on: {self.watch_path}")
        else:
            logger.warning(f"Watchdog watch path does not exist: {self.watch_path}")

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            logger.info("Watchdog observer stopped.")
