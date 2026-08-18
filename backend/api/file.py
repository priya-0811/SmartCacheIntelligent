import os
import time
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Response
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import FileMetadata, AccessLog, CacheEvent
from backend.cache.ram_cache import ram_cache
from backend.predictor.markov_predictor import markov_predictor
from backend.workers.background_manager import preload_queue

logger = logging.getLogger("smartcache.api.file")
router = APIRouter(tags=["File Operations"])

# Process-level state to track sequence of accesses: A -> B
_last_accessed_file: str | None = None

def _update_db_async(
    file_path: str,
    latency_ms: float,
    cache_status: str,
    prev_file: str | None,
    client_id: str = "client-1"
):
    """
    Asynchronous background DB updater to avoid blocking file read responses.
    """
    from backend.database.database import SessionLocal
    db = SessionLocal()
    try:
        abs_path = os.path.abspath(file_path)
        filename = os.path.basename(abs_path)
        filesize = os.path.getsize(abs_path) if os.path.exists(abs_path) else 0

        # Find or create FileMetadata
        meta = db.query(FileMetadata).filter_by(filepath=abs_path).first()
        if not meta:
            meta = FileMetadata(
                filepath=abs_path,
                filename=filename,
                filesize=filesize,
                created_at=datetime.utcnow()
            )
            db.add(meta)
            db.flush()

        meta.access_count += 1
        meta.last_access = datetime.utcnow()

        if cache_status == "CACHE_HIT":
            meta.cache_hits += 1
        else:
            meta.cache_misses += 1

        # Record access log
        log = AccessLog(
            file_id=meta.id,
            timestamp=datetime.utcnow(),
            latency_ms=latency_ms,
            cache_status=cache_status,
            client_id=client_id
        )
        db.add(log)

        # Record cache event
        event = CacheEvent(
            file_id=meta.id,
            event_type=cache_status,
            timestamp=datetime.utcnow()
        )
        db.add(event)

        # Record Markov transition if previous file exists
        if prev_file and prev_file != abs_path and os.path.exists(prev_file):
            markov_predictor.record_transition(db, prev_file, abs_path)

        db.commit()

        # Check Markov predictions for next file to preload
        predictions = markov_predictor.get_predictions(db, abs_path)
        for next_file, prob in predictions:
            if next_file not in ram_cache._cache:
                logger.info(f"Markov prediction triggered: P({os.path.basename(next_file)} | {filename}) = {prob:.2f} >= threshold. Queueing background preload.")
                preload_queue.put(next_file)

    except Exception as e:
        logger.error(f"Error in async DB updater: {e}")
        db.rollback()
    finally:
        db.close()

@router.get("/file")
def get_file(
    path: str = Query(..., description="Absolute or relative file path to read"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    client_id: str = Query("client-1", description="Client identifier")
):
    global _last_accessed_file
    
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
        raise HTTPException(status_code=404, detail=f"File not found on disk: {path}")

    previous_file = _last_accessed_file
    _last_accessed_file = abs_path

    # Step 1: Check RAM cache
    hit_result = ram_cache.get(abs_path)

    if hit_result is not None:
        # CACHE HIT
        binary_content, latency_ms = hit_result
        
        # Async DB update without blocking response
        background_tasks.add_task(
            _update_db_async,
            file_path=abs_path,
            latency_ms=latency_ms,
            cache_status="CACHE_HIT",
            prev_file=previous_file,
            client_id=client_id
        )

        return Response(
            content=binary_content,
            media_type="application/octet-stream",
            headers={
                "X-SmartCache-Status": "HIT",
                "X-SmartCache-Latency-MS": f"{latency_ms:.4f}",
                "X-SmartCache-File": os.path.basename(abs_path)
            }
        )

    # Step 2: CACHE MISS - Read from Disk
    start_time = time.perf_counter()
    try:
        with open(abs_path, "rb") as f:
            binary_content = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file from disk: {str(e)}")

    latency_ms = (time.perf_counter() - start_time) * 1000.0

    # Step 3: Put into RAM Cache
    ram_cache.put(abs_path, binary_content)

    # Async DB update
    background_tasks.add_task(
        _update_db_async,
        file_path=abs_path,
        latency_ms=latency_ms,
        cache_status="CACHE_MISS",
        prev_file=previous_file,
        client_id=client_id
    )

    return Response(
        content=binary_content,
        media_type="application/octet-stream",
        headers={
            "X-SmartCache-Status": "MISS",
            "X-SmartCache-Latency-MS": f"{latency_ms:.4f}",
            "X-SmartCache-File": os.path.basename(abs_path)
        }
    )
