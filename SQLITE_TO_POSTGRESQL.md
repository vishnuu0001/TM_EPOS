# SQLite to PostgreSQL Migration Guide

## When to Migrate

Consider migrating from SQLite to PostgreSQL when:

- **User Load**: More than 100 concurrent users
- **Data Volume**: Database exceeds 10GB
- **Write Frequency**: Heavy write operations (>1000 writes/min)
- **Replication Needed**: Requires read replicas or high availability
- **Advanced Features**: Need full-text search, advanced JSON queries, or stored procedures

## Migration Steps

### 1. Install PostgreSQL

**Windows:**
```powershell
# Download and install from https://www.postgresql.org/download/windows/
# Or use chocolatey:
choco install postgresql
```

**Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create PostgreSQL Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database and user
CREATE DATABASE epos_db;
CREATE USER epos_user WITH PASSWORD 'epos_password';
GRANT ALL PRIVILEGES ON DATABASE epos_db TO epos_user;
\q
```

### 3. Export Data from SQLite

```bash
# Install sqlite3 command line tool (usually pre-installed)
cd backend/data

# Export schema and data
sqlite3 epos.db .dump > epos_dump.sql
```

### 4. Convert SQL Dump for PostgreSQL

Create a Python script `convert_dump.py`:

```python
import re

def convert_sqlite_to_postgres(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Remove SQLite-specific commands
    content = re.sub(r'BEGIN TRANSACTION;', 'BEGIN;', content)
    content = re.sub(r'PRAGMA.*?;', '', content)
    
    # Convert AUTOINCREMENT to SERIAL
    content = re.sub(
        r'INTEGER PRIMARY KEY AUTOINCREMENT',
        'SERIAL PRIMARY KEY',
        content
    )
    
    # Convert datetime
    content = re.sub(r'DATETIME', 'TIMESTAMP', content)
    
    # Write converted content
    with open(output_file, 'w') as f:
        f.write(content)

if __name__ == '__main__':
    convert_sqlite_to_postgres('epos_dump.sql', 'postgres_dump.sql')
    print("Conversion complete!")
```

Run the conversion:
```bash
python convert_dump.py
```

### 5. Import to PostgreSQL

```bash
psql -U epos_user -d epos_db -f postgres_dump.sql
```

### 6. Update Configuration

Update `backend/.env`:

```bash
# Change from:
DATABASE_URL=sqlite:///./backend/data/epos.db

# To:
DATABASE_URL=postgresql://epos_user:epos_password@localhost:5432/epos_db
```

### 7. Update Requirements

Add PostgreSQL driver to `backend/requirements.txt`:

```
psycopg2-binary==2.9.9
```

Install:
```bash
pip install psycopg2-binary
```

### 8. Update Database Configuration

Update `backend/shared/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings

# Create database engine
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=10,  # PostgreSQL can handle connection pooling
    max_overflow=20,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 9. Update Docker Compose

Update `docker-compose.yml` to add PostgreSQL service:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: epos-postgres
    environment:
      POSTGRES_DB: epos_db
      POSTGRES_USER: epos_user
      POSTGRES_PASSWORD: epos_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U epos_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - epos-network

  # Update all services to use PostgreSQL
  api-gateway:
    environment:
      - DATABASE_URL=postgresql://epos_user:epos_password@postgres:5432/epos_db
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
```

### 10. Test Migration

```bash
# Restart services
docker-compose down
docker-compose up -d

# Test API
curl http://localhost:8000/api/health

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin@epos.com&password=Admin@123"
```

## Performance Optimization for PostgreSQL

### Add Indexes

```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_employee_id ON users(employee_id);
CREATE INDEX idx_maintenance_requests_status ON maintenance_requests(status);
CREATE INDEX idx_maintenance_requests_created ON maintenance_requests(created_at);
```

### Enable Connection Pooling

Update `backend/shared/database.py`:

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,        # Increase pool size
    max_overflow=40,      # More overflow connections
    pool_timeout=30,      # Wait time for connection
    pool_recycle=3600,    # Recycle connections every hour
    pool_pre_ping=True    # Verify connections
)
```

### Configure PostgreSQL

Edit `postgresql.conf`:

```conf
# Increase memory
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB

# Increase connections
max_connections = 200

# Enable query optimization
random_page_cost = 1.1
effective_io_concurrency = 200
```

## Rollback Plan

If issues occur, you can rollback to SQLite:

1. Stop all services
2. Restore SQLite database from backup
3. Update `DATABASE_URL` back to SQLite
4. Restart services

```bash
# Backup before migration!
cp backend/data/epos.db backend/data/epos_backup.db
```

## Comparison: SQLite vs PostgreSQL

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| **Setup** | None required | Requires installation |
| **Concurrent Writes** | Limited (1 writer) | Excellent (many writers) |
| **Concurrent Reads** | Good | Excellent |
| **Max Database Size** | 281 TB (practical: ~1GB) | Unlimited |
| **Memory Usage** | Very low | Higher |
| **Backup** | Copy file | pg_dump |
| **Replication** | None | Built-in |
| **Full-Text Search** | Basic | Advanced |
| **Cost** | Free | Free |
| **Hosting** | Embedded | Requires server |

## Conclusion

SQLite is perfect for:
- Development and testing
- Small to medium deployments (<100 users)
- Applications with read-heavy workloads
- Embedded applications

PostgreSQL is better for:
- Production environments with high traffic
- Multiple concurrent writers
- Large datasets (>10GB)
- Advanced database features
- High availability requirements

The application is designed to work with both - choose based on your needs!
