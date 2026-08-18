import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.database import init_db

# Initialize database tables for tests
init_db()

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["system"] == "SmartCache"

def test_cache_stats_endpoint():
    response = client.get("/cache/stats")
    assert response.status_code == 200
    data = response.json()
    assert "hit_count" in data
    assert "memory_usage_mb" in data

def test_cache_clear_endpoint():
    response = client.post("/cache/clear")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_cache_config_endpoint():
    payload = {
        "max_size_mb": 150.0,
        "eviction_algorithm": "lru",
        "preload_threshold": 0.75
    }
    response = client.post("/cache/config", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["updated_settings"]["eviction_algorithm"] == "lru"

def test_telemetry_history_endpoint():
    response = client.get("/telemetry/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_predictor_transitions_endpoint():
    response = client.get("/predictor/transitions")
    assert response.status_code == 200
    assert "transitions" in response.json()
