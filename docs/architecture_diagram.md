# SmartCache System Architecture Diagram

The SmartCache architecture consists of a high-performance in-memory layer (Python process memory with `threading.RLock`), backed by MySQL metadata tracking, watchdog file observer, background workers, Markov predictive preloader, and an interactive React dashboard.

```mermaid
graph TD
    Client[React Dashboard / REST Client] -->|GET /file| FastAPI[FastAPI Controller]
    
    subgraph RAM Caching Layer
        FastAPI -->|1. Check Cache| RAMCache[RAM Cache Manager]
        RAMCache -->|Lock Protected Dict| Entries[CacheEntry Binary Storage]
        RAMCache -->|Capacity Exceeded| EvictionEngine[Eviction Engine]
        EvictionEngine -->|Policy: LRU/LFU/Hybrid| Evicted[Evict Victim File]
    end

    subgraph Storage & Invalidation
        FastAPI -->|2. Disk Miss Read| Disk[Local Disk Storage]
        Watchdog[Watchdog Observer] -->|Source File Change| RAMCache
    end

    subgraph Background Workers & Markov Predictor
        FastAPI -->|3. Record Sequence A -> B| Markov[Markov Chain Predictor]
        Markov -->|P >= 0.70| PreloadQueue[Background Preload Queue]
        PreloadQueue -->|Worker 2| PreloaderWorker[Predictive Preloader Worker]
        PreloaderWorker -->|Background Load| RAMCache
        
        TelemetryWorker[Worker 1: Telemetry Updater] -->|Snapshot Every 5s| Telemetry[Telemetry Module]
        CleanupWorker[Worker 3: Periodic Cleanup] -->|Purge Stale Logs| DB[(MySQL Database)]
    end

    subgraph Database Layer (MySQL)
        FastAPI -->|Async Log & Stats| DB
        Telemetry -->|Store History| DB
        DB -->|files, access_logs, transitions, cache_events, telemetry_logs| DB
    end
```
