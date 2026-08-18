from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import AccessLog, CacheEvent, FileMetadata
from backend.telemetry.telemetry_service import telemetry_service

router = APIRouter(tags=["Telemetry & Monitoring"])

@router.get("/telemetry/history")
def get_telemetry_history(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Returns historical telemetry snapshot metrics for rendering time-series graphs.
    """
    return telemetry_service.get_history(db, limit=limit)

@router.get("/logs/access")
def get_access_logs(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Returns recent file access logs with response latencies and hit/miss statuses.
    """
    logs = (
        db.query(AccessLog, FileMetadata)
        .join(FileMetadata, AccessLog.file_id == FileMetadata.id)
        .order_by(AccessLog.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": log.AccessLog.id,
            "filename": log.FileMetadata.filename,
            "filepath": log.FileMetadata.filepath,
            "timestamp": log.AccessLog.timestamp.isoformat(),
            "latency_ms": round(log.AccessLog.latency_ms, 4),
            "cache_status": log.AccessLog.cache_status,
            "client_id": log.AccessLog.client_id
        }
        for log in logs
    ]

@router.get("/logs/events")
def get_cache_events(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Returns recent cache events (PRELOAD, EVICT, CACHE_HIT, CACHE_MISS).
    """
    events = (
        db.query(CacheEvent, FileMetadata)
        .outerjoin(FileMetadata, CacheEvent.file_id == FileMetadata.id)
        .order_by(CacheEvent.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": event.CacheEvent.id,
            "event_type": event.CacheEvent.event_type,
            "timestamp": event.CacheEvent.timestamp.isoformat(),
            "filename": event.FileMetadata.filename if event.FileMetadata else "System",
            "filepath": event.FileMetadata.filepath if event.FileMetadata else ""
        }
        for event in events
    ]
