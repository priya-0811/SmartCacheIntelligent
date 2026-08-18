import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App config
    PROJECT_NAME: str = "SmartCache"
    VERSION: str = "1.0.0"
    API_PREFIX: str = ""
    DEBUG: bool = True
    
    # Cache settings
    MAX_CACHE_SIZE_MB: float = 100.0  # Configurable limit in MB
    EVICTION_ALGORITHM: str = "hybrid"  # lru, lfu, hybrid
    PRELOAD_THRESHOLD: float = 0.70    # Markov prediction probability threshold
    
    # Watchdog file monitoring directory
    WATCH_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    # Database configuration
    DB_USER: str = os.getenv("MYSQL_USER", "root")
    DB_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    DB_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    DB_PORT: str = os.getenv("MYSQL_PORT", "3306")
    DB_NAME: str = os.getenv("MYSQL_DATABASE", "smartcache_db")
    
    USE_MYSQL: bool = os.getenv("USE_MYSQL", "false").lower() == "true"
    
    @property
    def DATABASE_URL(self) -> str:
        if self.USE_MYSQL:
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartcache.db")
            return f"sqlite:///{db_path}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
