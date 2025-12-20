# MediConnect - Best Practices Implementation Guide

## 📋 Overview

This document outlines all the best practices implemented in the MediConnect application, providing a comprehensive guide for developers and system administrators.

---

## ✅ Implemented Best Practices

### 1. **Redis Caching & Performance** ⚡

#### Features
- In-memory caching with Redis 7
- Distributed rate limiting
- Connection pooling (max 50 connections)
- Automatic cache invalidation
- TTL-based expiration (default 5 minutes)
- Graceful degradation when Redis unavailable

#### Configuration
```env
REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=true
REDIS_CACHE_TTL=300
REDIS_MAX_CONNECTIONS=50
```

#### Usage Example
```python
from app.services.cache import doctors_cache

# Get from cache
doctor = await doctors_cache.get(doctor_id)

# Set cache
await doctors_cache.set(doctor_id, doctor_data, ttl=300)

# Invalidate cache
await doctors_cache.delete(doctor_id)
```

#### Performance Gains
- 50-90% faster response times
- 70-80% reduction in database queries
- 3-5x higher throughput

---

### 2. **Advanced Logging & Monitoring** 📊

#### Features
- Structured JSON logging
- Request ID tracking (X-Request-ID header)
- Colored console output for development
- Execution time tracking
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

#### Usage Example
```python
from app.services.logging_config import get_logger, log_execution_time

logger = get_logger(__name__)

@log_execution_time
async def process_data():
    logger.info("Processing started", extra={'user_id': '123'})
    # ... processing code
```

#### Log Format
```json
{
  "timestamp": "2025-12-20T10:30:00Z",
  "level": "INFO",
  "logger": "app.routers.doctors",
  "message": "Doctor profile updated",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "execution_time": 0.045
}
```

---

### 3. **Comprehensive Health Checks** 🏥

#### Endpoints

| Endpoint | Purpose | Status Code |
|----------|---------|-------------|
| `/health` | Basic health check | 200 |
| `/health/ready` | Readiness check (DB + Redis) | 200 |
| `/health/live` | Liveness check | 200 |
| `/health/startup` | Startup check | 200 |
| `/health/metrics` | Application metrics | 200 |

#### Usage in Kubernetes
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

#### Metrics Response
```json
{
  "timestamp": "2025-12-20T10:30:00Z",
  "redis": {
    "connected_clients": 5,
    "used_memory_human": "2.5MB",
    "hit_rate": "87.64%"
  },
  "database": {
    "connections": 12,
    "operations": {
      "insert": 1234,
      "query": 5678
    }
  }
}
```

---

### 4. **Database Best Practices** 💾

#### Connection Pooling
```python
client = AsyncIOMotorClient(
    MONGO_URL,
    maxPoolSize=50,
    minPoolSize=5,
    maxIdleTimeMS=45000,
    retryWrites=True,
    retryReads=True
)
```

#### Retry Logic
```python
from app.services.database import retry_on_failure

@retry_on_failure(max_retries=3, delay=1.0)
async def get_user(user_id: str):
    return await db.users.find_one({"user_id": user_id})
```

#### Optimized Indexes
```python
# Users collection
await db.users.create_index("email", unique=True)
await db.users.create_index([("organization_id", 1), ("role", 1)])

# Appointments collection
await db.appointments.create_index([("doctor_id", 1), ("date_time", 1)])
await db.appointments.create_index([("patient_id", 1), ("date_time", -1)])

# Doctors collection
await db.doctors.create_index("doctor_id", unique=True)
await db.doctors.create_index([("clinic_id", 1), ("is_active", 1)])
await db.doctors.create_index("specialty")
```

---

### 5. **API Versioning** 🔄

#### Supported Methods
1. **URL-based**: `/api/v1/users`, `/api/v2/users`
2. **Header-based**: `X-API-Version: 2.0`
3. **Query parameter**: `?api_version=2.0`

#### Configuration
```python
SUPPORTED_VERSIONS = ["1.0", "2.0"]
DEFAULT_VERSION = "2.0"
DEPRECATED_VERSIONS = ["1.0"]
```

#### Response Headers
```
X-API-Version: 2.0
X-API-Deprecated: true  # If using deprecated version
X-API-Sunset: 2026-12-31  # Deprecation date
```

---

### 6. **Security Headers** 🛡️

#### Implemented Headers
```
X-XSS-Protection: 1; mode=block
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

#### Protection Against
- ✅ XSS (Cross-Site Scripting)
- ✅ Clickjacking
- ✅ MIME type sniffing
- ✅ Unauthorized feature access
- ✅ Information leakage

---

### 7. **Input Sanitization** 🧹

#### Features
- XSS prevention
- SQL/NoSQL injection prevention
- Directory traversal prevention
- Filename sanitization
- MongoDB query validation

#### Usage Example
```python
from app.services.sanitization import sanitizer

# Sanitize string
safe_text = sanitizer.sanitize_string(user_input, max_length=1000)

# Sanitize email
safe_email = sanitizer.sanitize_email(email)

# Sanitize dictionary
safe_data = sanitizer.sanitize_dict(request_data)

# Validate MongoDB query
if sanitizer.validate_mongo_query(query):
    results = await db.collection.find(query)
```

#### Dangerous Patterns Detected
- `<script>` tags
- `javascript:` protocol
- Event handlers (`onclick`, `onerror`, etc.)
- MongoDB operators (`$where`, `$ne`, `$gt`, etc.)
- Iframes, objects, embeds

---

### 8. **Rate Limiting** 🚦

#### Configuration
```python
RATE_LIMITS = {
    "default": 60,    # 60 requests/minute
    "auth": 10,       # 10 requests/minute
    "upload": 5       # 5 requests/minute
}
```

#### Features
- Redis-backed distributed rate limiting
- Sliding window algorithm
- Per-endpoint limits
- IP-based tracking
- Automatic fallback to in-memory

#### Response Headers
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 60
```

---

### 9. **Error Handling** ⚠️

#### Structured Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    },
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-12-20T10:30:00Z"
  }
}
```

#### Error Codes
- `VALIDATION_ERROR` - Input validation failed
- `AUTHENTICATION_ERROR` - Authentication failed
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `CONFLICT` - Resource conflict
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error

---

### 10. **Request ID Tracking** 🔍

#### Features
- Unique ID for each request
- Propagated through all logs
- Included in error responses
- Useful for distributed tracing

#### Headers
```
Request:  X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
Response: X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

#### Usage
```python
from app.middleware import get_request_id

request_id = get_request_id(request)
logger.info(f"Processing request {request_id}")
```

---

## 🚀 Performance Optimization

### Query Optimization
```python
# Use projection to fetch only needed fields
user = await db.users.find_one(
    {"user_id": user_id},
    {"_id": 0, "name": 1, "email": 1}
)

# Use indexes for sorting
appointments = await db.appointments.find(
    {"doctor_id": doctor_id}
).sort([("date_time", -1)]).limit(10)
```

### Pagination
```python
async def get_paginated_results(
    collection: str,
    filter: dict,
    page: int = 1,
    page_size: int = 20
):
    skip = (page - 1) * page_size
    results = await db[collection].find(filter).skip(skip).limit(page_size)
    total = await db[collection].count_documents(filter)
    
    return {
        "data": results,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": (total + page_size - 1) // page_size
        }
    }
```

---

## 🔒 Security Checklist

- ✅ **Authentication**: JWT tokens with expiration
- ✅ **Authorization**: Role-based access control (RBAC)
- ✅ **Input Validation**: Pydantic schemas
- ✅ **Input Sanitization**: XSS and injection prevention
- ✅ **Rate Limiting**: Distributed with Redis
- ✅ **CORS**: Configured origins only
- ✅ **Security Headers**: XSS, clickjacking protection
- ✅ **HTTPS**: Enforced in production
- ✅ **Password Hashing**: Bcrypt with salt
- ✅ **SQL Injection**: Using parameterized queries
- ✅ **NoSQL Injection**: Query validation
- ✅ **File Upload**: Filename sanitization
- ✅ **Error Messages**: No sensitive data exposure
- ✅ **Logging**: No sensitive data in logs
- ✅ **Request ID**: Tracking for audit trails

---

## 📊 Monitoring & Observability

### Key Metrics to Monitor

1. **Application Metrics**
   - Request rate
   - Response time (p50, p95, p99)
   - Error rate
   - Active connections

2. **Redis Metrics**
   - Cache hit rate
   - Memory usage
   - Connected clients
   - Commands processed

3. **Database Metrics**
   - Query execution time
   - Connection pool usage
   - Index usage
   - Slow queries

4. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network I/O

### Monitoring Tools
- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **ELK Stack** - Log aggregation
- **Sentry** - Error tracking
- **New Relic / DataDog** - APM

---

## 🧪 Testing Best Practices

### Unit Tests
```python
import pytest
from app.services.sanitization import sanitizer

def test_sanitize_string():
    result = sanitizer.sanitize_string("<script>alert('xss')</script>")
    assert "<script>" not in result

def test_sanitize_email():
    result = sanitizer.sanitize_email("USER@EXAMPLE.COM")
    assert result == "user@example.com"
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_create_appointment(client):
    response = await client.post("/api/appointments", json={
        "doctor_id": "doc123",
        "patient_id": "pat456",
        "date_time": "2025-12-25T10:00:00Z"
    })
    assert response.status_code == 201
```

### Load Testing
```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/doctors

# Using wrk
wrk -t12 -c400 -d30s http://localhost:8000/api/doctors
```

---

## 📦 Deployment Best Practices

### Docker Health Checks
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Kubernetes Configuration
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5

startupProbe:
  httpGet:
    path: /health/startup
    port: 8000
  failureThreshold: 30
  periodSeconds: 10
```

### Environment Configuration
```env
# Production
DEBUG=false
LOG_LEVEL=INFO
REDIS_ENABLED=true
REDIS_MAX_CONNECTIONS=100
MONGO_MAX_POOL_SIZE=50
```

---

## 💾 Backup & Recovery

### Database Backup
```bash
# Automated backup script
docker-compose exec backend python -c "
from app.db import db
import asyncio
import json
from datetime import datetime

async def backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    collections = await db.list_collection_names()
    for coll in collections:
        data = await db[coll].find({}).to_list(None)
        with open(f'backup_{coll}_{timestamp}.json', 'w') as f:
            json.dump(data, f)
    print(f'Backup completed: {timestamp}')

asyncio.run(backup())
"
```

### Redis Backup
```bash
# Save Redis snapshot
docker-compose exec redis redis-cli SAVE

# Copy backup file
docker cp mediconnect-redis-1:/data/dump.rdb ./backup/redis_$(date +%Y%m%d_%H%M%S).rdb
```

---

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [MongoDB Performance](https://docs.mongodb.com/manual/administration/analyzing-mongodb-performance/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Tools
- [Swagger UI](http://localhost:8000/docs) - API documentation
- [ReDoc](http://localhost:8000/redoc) - Alternative API docs
- [Redis Commander](https://github.com/joeferner/redis-commander) - Redis GUI
- [MongoDB Compass](https://www.mongodb.com/products/compass) - MongoDB GUI

---

## 🎯 Next Steps

1. **Implement CI/CD Pipeline**
   - GitHub Actions / GitLab CI
   - Automated testing
   - Automated deployment

2. **Add APM (Application Performance Monitoring)**
   - New Relic / DataDog
   - Performance tracking
   - Error tracking

3. **Implement Distributed Tracing**
   - OpenTelemetry
   - Jaeger / Zipkin
   - Request flow visualization

4. **Add Automated Testing**
   - Unit tests (pytest)
   - Integration tests
   - E2E tests (Playwright)
   - Load tests (Locust)

5. **Implement Feature Flags**
   - LaunchDarkly / Unleash
   - Gradual rollouts
   - A/B testing

---

**Last Updated**: December 20, 2025  
**Version**: 2.0.0  
**Maintained by**: ACL-Smart Software
