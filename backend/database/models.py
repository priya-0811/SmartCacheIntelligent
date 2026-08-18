from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.database import Base

class FileMetadata(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filepath = Column(String(512), unique=True, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    filesize = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    access_count = Column(Integer, default=0, nullable=False)
    last_access = Column(DateTime, nullable=True)
    cache_hits = Column(Integer, default=0, nullable=False)
    cache_misses = Column(Integer, default=0, nullable=False)

    access_logs = relationship("AccessLog", back_populates="file", cascade="all, delete-orphan")
    cache_events = relationship("CacheEvent", back_populates="file", cascade="all, delete-orphan")

class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    latency_ms = Column(Float, nullable=False)
    cache_status = Column(String(50), nullable=False)  # CACHE_HIT, CACHE_MISS
    client_id = Column(String(100), default="client-1", nullable=False)

    file = relationship("FileMetadata", back_populates="access_logs")

class Transition(Base):
    __tablename__ = "transitions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    previous_file = Column(String(512), index=True, nullable=False)
    next_file = Column(String(512), index=True, nullable=False)
    transition_count = Column(Integer, default=0, nullable=False)

class CacheEvent(Base):
    __tablename__ = "cache_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey("files.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(50), nullable=False)  # CACHE_HIT, CACHE_MISS, PRELOAD, EVICT, INSERT
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    file = relationship("FileMetadata", back_populates="cache_events")

class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    cache_hits = Column(Integer, default=0, nullable=False)
    cache_misses = Column(Integer, default=0, nullable=False)
    hit_ratio = Column(Float, default=0.0, nullable=False)
    miss_ratio = Column(Float, default=0.0, nullable=False)
    avg_read_latency = Column(Float, default=0.0, nullable=False)
    eviction_count = Column(Integer, default=0, nullable=False)
    preload_accuracy = Column(Float, default=0.0, nullable=False)
    current_ram_usage = Column(Float, default=0.0, nullable=False)
    cached_file_count = Column(Integer, default=0, nullable=False)
