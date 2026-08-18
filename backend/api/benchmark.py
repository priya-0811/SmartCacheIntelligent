import os
import glob
import time
import logging
from fastapi import APIRouter, Query
from backend.cache.ram_cache import ram_cache
from backend.config import settings

logger = logging.getLogger("smartcache.api.benchmark")
router = APIRouter(prefix="/benchmark", tags=["Performance Evaluation"])

@router.post("/run")
def run_benchmark(
    iterations: int = Query(50, ge=10, le=500, description="Number of file read iterations to simulate")
):
    """
    Performance Evaluation Benchmark.
    Compares direct cold disk I/O latency against SmartCache RAM latency.
    """
    watch_dir = settings.WATCH_DIR
    target_files = glob.glob(os.path.join(watch_dir, "*.*"))

    if not target_files:
        # Fallback: create mock files if none exist
        os.makedirs(watch_dir, exist_ok=True)
        for i in range(5):
            fname = os.path.join(watch_dir, f"sample_{i+1}.txt")
            with open(fname, "w") as f:
                f.write(f"Sample benchmark content for file {i+1}\n" * 500)
            target_files.append(fname)

    # 1. Cold Disk Read Test (Without SmartCache)
    disk_latencies = []
    for i in range(iterations):
        target = target_files[i % len(target_files)]
        t0 = time.perf_counter()
        with open(target, "rb") as f:
            _ = f.read()
        disk_latencies.append((time.perf_counter() - t0) * 1000.0)

    avg_disk_latency = sum(disk_latencies) / len(disk_latencies)

    # 2. Warm RAM Cache Test (With SmartCache)
    # Pre-populate RAM cache
    for target in target_files:
        with open(target, "rb") as f:
            ram_cache.put(target, f.read())

    ram_latencies = []
    for i in range(iterations):
        target = target_files[i % len(target_files)]
        hit_res = ram_cache.get(target)
        if hit_res:
            ram_latencies.append(hit_res[1])
        else:
            # Fallback if evicted
            t0 = time.perf_counter()
            with open(target, "rb") as f:
                ram_cache.put(target, f.read())
            ram_latencies.append((time.perf_counter() - t0) * 1000.0)

    avg_ram_latency = sum(ram_latencies) / len(ram_latencies)

    # 3. Calculate Performance Metrics
    latency_reduction_ms = max(0.0, avg_disk_latency - avg_ram_latency)
    speedup_pct = ((avg_disk_latency - avg_ram_latency) / avg_disk_latency * 100.0) if avg_disk_latency > 0 else 0.0
    hit_ratio_pct = (ram_cache.total_hits / max(1, (ram_cache.total_hits + ram_cache.total_misses))) * 100.0
    memory_savings_mb = ram_cache.get_current_bytes() / (1024 * 1024)

    return {
        "status": "success",
        "iterations": iterations,
        "without_smartcache": {
            "average_disk_read_time_ms": round(avg_disk_latency, 4)
        },
        "with_smartcache": {
            "average_ram_read_time_ms": round(avg_ram_latency, 4)
        },
        "results": {
            "speedup_percentage": round(max(0.0, speedup_pct), 2),
            "hit_ratio_percentage": round(hit_ratio_pct, 2),
            "latency_reduction_ms": round(latency_reduction_ms, 4),
            "memory_savings_mb": round(memory_savings_mb, 2)
        }
    }
