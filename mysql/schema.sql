-- SmartCache Database Schema for MySQL 8.0+

CREATE DATABASE IF NOT EXISTS smartcache_db;
USE smartcache_db;

-- Table: files
CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filepath VARCHAR(512) NOT NULL UNIQUE,
    filename VARCHAR(255) NOT NULL,
    filesize INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    access_count INT DEFAULT 0 NOT NULL,
    last_access DATETIME NULL,
    cache_hits INT DEFAULT 0 NOT NULL,
    cache_misses INT DEFAULT 0 NOT NULL,
    INDEX idx_filepath (filepath)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: access_logs
CREATE TABLE IF NOT EXISTS access_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    latency_ms FLOAT NOT NULL,
    cache_status VARCHAR(50) NOT NULL,
    client_id VARCHAR(100) DEFAULT 'client-1' NOT NULL,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    INDEX idx_timestamp (timestamp),
    INDEX idx_file_id (file_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: transitions
CREATE TABLE IF NOT EXISTS transitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    previous_file VARCHAR(512) NOT NULL,
    next_file VARCHAR(512) NOT NULL,
    transition_count INT DEFAULT 0 NOT NULL,
    INDEX idx_previous_file (previous_file),
    INDEX idx_next_file (next_file)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: cache_events
CREATE TABLE IF NOT EXISTS cache_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT NULL,
    event_type VARCHAR(50) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE SET NULL,
    INDEX idx_event_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: telemetry_logs
CREATE TABLE IF NOT EXISTS telemetry_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cache_hits INT DEFAULT 0 NOT NULL,
    cache_misses INT DEFAULT 0 NOT NULL,
    hit_ratio FLOAT DEFAULT 0.0 NOT NULL,
    miss_ratio FLOAT DEFAULT 0.0 NOT NULL,
    avg_read_latency FLOAT DEFAULT 0.0 NOT NULL,
    eviction_count INT DEFAULT 0 NOT NULL,
    preload_accuracy FLOAT DEFAULT 0.0 NOT NULL,
    current_ram_usage FLOAT DEFAULT 0.0 NOT NULL,
    cached_file_count INT DEFAULT 0 NOT NULL,
    INDEX idx_telemetry_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
