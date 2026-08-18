# SmartCache Database Schema Specification

The database maintains file metadata, access logs, Markov state transitions, cache events, and historical telemetry snapshots.

---

## Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    files ||--o{ access_logs : "has logs"
    files ||--o{ cache_events : "generates events"

    files {
        int id PK
        string filepath UK
        string filename
        int filesize
        datetime created_at
        datetime updated_at
        int access_count
        datetime last_access
        int cache_hits
        int cache_misses
    }

    access_logs {
        int id PK
        int file_id FK
        datetime timestamp
        float latency_ms
        string cache_status
        string client_id
    }

    transitions {
        int id PK
        string previous_file
        string next_file
        int transition_count
    }

    cache_events {
        int id PK
        int file_id FK
        string event_type
        datetime timestamp
    }

    telemetry_logs {
        int id PK
        datetime timestamp
        int cache_hits
        int cache_misses
        float hit_ratio
        float miss_ratio
        float avg_read_latency
        int eviction_count
        float preload_accuracy
        float current_ram_usage
        int cached_file_count
    }
```
