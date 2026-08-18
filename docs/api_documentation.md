# SmartCache REST API Reference

All APIs return standardized JSON responses or binary streams. Automatically generated OpenAPI Swagger documentation is available at `/docs`.

---

## 1. File Access API

### `GET /file`
Reads file content. Serves directly from RAM cache if cached (`HIT`), otherwise loads from disk (`MISS`), updates RAM cache, and asynchronously logs metadata & triggers Markov preloading.

- **Parameters**:
  - `path` (string, required): Absolute or relative file path to read.
  - `client_id` (string, optional): Client ID requesting the file. Default: `client-1`.
- **Response**: Binary octet-stream with custom HTTP headers:
  - `X-SmartCache-Status`: `HIT` or `MISS`
  - `X-SmartCache-Latency-MS`: Read latency in milliseconds.
  - `X-SmartCache-File`: Filename.

---

## 2. Cache Controller APIs

### `POST /cache/clear`
Clears all binary content and metadata entries from RAM cache.

- **Response**:
  ```json
  {
    "status": "success",
    "message": "RAM cache successfully cleared."
  }
  ```

### `GET /cache/stats`
Returns live cache counters, memory utilization, latency metrics, and eviction counts.

- **Response**:
  ```json
  {
    "hit_count": 12,
    "miss_count": 4,
    "hit_ratio": 0.75,
    "miss_ratio": 0.25,
    "memory_usage_mb": 14.2,
    "max_memory_mb": 100.0,
    "memory_utilization_pct": 14.2,
    "cached_files_count": 4,
    "total_bytes": 14889500,
    "average_latency_ms": 0.1245,
    "eviction_count": 0,
    "eviction_algorithm": "hybrid",
    "process_ram_mb": 42.1,
    "system_ram_utilization_pct": 48.5
  }
  ```

### `GET /cache/files`
Returns detailed metadata for all files currently resident in RAM memory.

### `POST /cache/config`
Updates cache max size, eviction policy (`lru`, `lfu`, `hybrid`), or preloader threshold dynamically.

- **Request Body**:
  ```json
  {
    "max_size_mb": 200.0,
    "eviction_algorithm": "hybrid",
    "preload_threshold": 0.70
  }
  ```

---

## 3. Telemetry & Logs APIs

### `GET /telemetry/history`
Returns time-series telemetry snapshot history for Chart.js dashboard.

### `GET /logs/access`
Returns recent access log entries with response latency and `CACHE_HIT` / `CACHE_MISS` status.

### `GET /logs/events`
Returns recent cache events (`CACHE_HIT`, `CACHE_MISS`, `PRELOAD`, `EVICT`, `INSERT`).

---

## 4. Predictive Preloader APIs

### `GET /predictor/transitions`
Returns Markov Chain transition counts and state transition probabilities $P(B|A)$.

### `GET /predictor/predict?filepath=...`
Predicts next files likely to be accessed given `filepath`.

---

## 5. Performance Evaluation Benchmark API

### `POST /benchmark/run?iterations=100`
Executes load test comparing cold disk I/O against SmartCache RAM latency. Returns speedup %, latency reduction ms, and memory savings.
