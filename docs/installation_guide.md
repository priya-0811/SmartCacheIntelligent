# Installation & Deployment Guide

## Prerequisites
- **Python**: 3.12 or higher
- **Node.js**: 18.x or 20.x
- **MySQL**: 8.0 (optional, fallback to SQLite enabled by default)
- **Docker & Docker Compose** (optional for containerized deployment)

---

## Step-by-Step Local Environment Setup

### 1. Clone & Navigate to Project Directory
```bash
cd C:\Users\priya\.gemini\antigravity\scratch\smartcache
```

### 2. Configure Environment Variables (`.env`)
Create a `.env` file in the project root:
```env
PROJECT_NAME="SmartCache"
MAX_CACHE_SIZE_MB=100.0
EVICTION_ALGORITHM="hybrid"
PRELOAD_THRESHOLD=0.70

# MySQL Configuration (Set USE_MYSQL=true for production MySQL)
USE_MYSQL=false
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=smartcache_db
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start FastAPI Backend
```bash
python -m backend.main
```
Backend will start at `http://localhost:8000`. Swagger API documentation is available at `http://localhost:8000/docs`.

### 5. Install & Launch Frontend Dashboard
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
Dashboard will start at `http://localhost:3000`.

---

## Docker Deployment

To launch the complete multi-tier system with MySQL 8.0, Python FastAPI backend, and React Nginx frontend:

```bash
docker-compose up --build -d
```

To stop containers:
```bash
docker-compose down -v
```
