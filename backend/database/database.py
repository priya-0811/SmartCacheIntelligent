from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

# SQLite connection args if using sqlite
connect_args = {"check_same_thread": False} if not settings.USE_MYSQL else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.database.models import FileMetadata, AccessLog, Transition, CacheEvent, TelemetryLog
    Base.metadata.create_all(bind=engine)
