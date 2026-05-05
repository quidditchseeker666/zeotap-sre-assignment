# Zeotap SRE/DevOps Assignment - Distributed Task Queue System

## 📋 Project Overview

A **production-ready, distributed task queue system** built with modern DevOps practices and technologies. This project demonstrates containerization, service orchestration, distributed processing, monitoring, and automation.

### ✨ Key Highlights

✅ **Distributed Task Processing** - Multiple workers handle tasks in parallel  
✅ **Asynchronous Job Queue** - Redis-based task queuing system  
✅ **Persistent Storage** - PostgreSQL for reliable data storage  
✅ **Load Balancing** - Nginx reverse proxy with security headers  
✅ **Monitoring** - Prometheus metrics collection and dashboard  
✅ **Health Checks** - Comprehensive service health monitoring  
✅ **CI/CD Pipeline** - GitHub Actions automated testing and building  
✅ **Production Ready** - Security, scalability, and reliability built-in  

---

## 🏗️ System Architecture┌─────────────────────────────────────────────────────────────┐
│ Load Balancer (Nginx) │
│ Port 8080 → 80 │
└────────────────────────┬────────────────────────────────────┘
│
┌───────────────┼───────────────┐
│ │ │
┌────▼────┐ ┌────▼────┐ ┌────▼────┐
│ API │ │ API │ │ API │
│ Server │ │ Server │ │ Server │
│ (Flask) │ │ (Flask) │ │ (Flask) │
│ Port 80 │ │ Port 80 │ │ Port 80 │
└────┬────┘ └────┬────┘ └────┬────┘
│ │ │
└───────────────┼───────────────┘
│
┌────▼─────┐
│ Redis │
│ Queue │
│ Port 6379│
└────┬─────┘
│
┌───────────────┼───────────────┐
│ │ │
┌────▼────┐ ┌────▼────┐ ┌────▼────┐
│ Worker │ │ Worker │ │ Worker │
│ (Python)│ │ (Python)│ │ (Python)│
└────┬────┘ └────┬────┘ └────┬────┘
│ │ │
└───────────────┼───────────────┘
│
┌─────▼──────┐
│ PostgreSQL │
│ Database │
│ Port 5432 │
└────────────┘


---

## 🔌 Ports & Access Points

| Service | External Port | Internal Port | Access URL |
|---------|--------------|---------------|------------|
| **Nginx (Load Balancer)** | 8080 | 80 | http://localhost:8080 |
| **API Server** | 5001 | 5000 | http://localhost:5001 |
| **PostgreSQL** | 5433 | 5432 | localhost:5433 |
| **Redis** | 6380 | 6379 | localhost:6380 |
| **Prometheus** | 9090 | 9090 | http://localhost:9090 |

---

## 📦 Installation & Setup

### Prerequisites

- Docker (v24.0+)
- Docker Compose (v2.0+)
- 2GB+ free RAM
- Linux/Arch Linux (tested)

### Quick Start (3 Steps)

**Step 1: Clone and Enter Directory**
```bash
git clone https://github.com/quidditchseeker666/zeotap-sre-assignment.git
cd zeotap-sre-assignment
Step 2: Copy Environment File

Bash

cp .env.example .env
Step 3: Start Services

Bash

docker compose up -d
✅ Verify Installation
Bash

# Wait for services to be healthy
sleep 60

# Check all services are running
docker compose ps

# Test health endpoint
curl http://localhost:8080/health

# Expected response:
# {"status": "healthy", "services": {"postgres": "healthy", "redis": "healthy"}, ...}
🧪 Testing the System
Test 1: Submit a Task
Bash

curl -s -X POST http://localhost:8080/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "calculate",
    "payload": {
      "numbers": [1, 2, 3, 4, 5],
      "operation": "sum"
    }
  }' | jq .
Expected Response:

JSON

{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Task submitted successfully"
}
Test 2: Check Task Status
Bash

# Wait for processing
sleep 3

# Get status (replace task_id with actual ID)
curl http://localhost:8080/api/tasks/550e8400-e29b-41d4-a716-446655440000 | jq .
Expected Response (Completed):

JSON

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "calculate",
  "status": "completed",
  "result": {
    "status": "success",
    "result": {
      "result": 15
    }
  }
}
Test 3: Try Different Task Types
Calculate Task (Math Operations):

Bash

curl -X POST http://localhost:8080/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "calculate",
    "payload": {
      "numbers": [10, 20, 30],
      "operation": "sum"
    }
  }' | jq .
Transform Task (String Operations):

Bash

curl -X POST http://localhost:8080/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "transform",
    "payload": {
      "data": "hello world",
      "operation": "uppercase"
    }
  }' | jq .
Aggregate Task (Data Aggregation):

Bash

curl -X POST http://localhost:8080/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "aggregate",
    "payload": {
      "items": ["apple", "banana", "apple", "cherry"]
    }
  }' | jq .
Test 4: List All Tasks
Bash

curl http://localhost:8080/api/tasks | jq .
📚 API Endpoints
Health Check
Endpoint: GET /health

Bash

curl http://localhost:8080/health
Response:

JSON

{
  "status": "healthy",
  "timestamp": "2026-05-05T12:00:00.000000",
  "services": {
    "redis": "healthy",
    "postgres": "healthy"
  },
  "queue_size": 0
}
Submit Task
Endpoint: POST /api/tasks

Headers:

text

Content-Type: application/json
Request Body:

JSON

{
  "task_type": "calculate|transform|aggregate",
  "payload": {
    "numbers": [...],
    "operation": "sum|product|average",
    "data": "string",
    "items": [...]
  }
}
Response:

JSON

{
  "task_id": "uuid",
  "status": "queued",
  "message": "Task submitted successfully"
}
Get Task Status
Endpoint: GET /api/tasks/<task_id>

Bash

curl http://localhost:8080/api/tasks/550e8400-e29b-41d4-a716-446655440000
Response:

JSON

{
  "id": "task_id",
  "task_type": "calculate",
  "payload": {...},
  "status": "pending|processing|completed",
  "result": {...},
  "created_at": "2026-05-05T...",
  "updated_at": "2026-05-05T...",
  "completed_at": "2026-05-05T..."
}
List Tasks
Endpoint: GET /api/tasks?page=1&per_page=10&status=completed

Bash

# List all tasks
curl http://localhost:8080/api/tasks

# Filter by status
curl http://localhost:8080/api/tasks?status=completed
curl http://localhost:8080/api/tasks?status=processing
curl http://localhost:8080/api/tasks?status=pending
📊 Monitoring & Metrics
Prometheus Dashboard
Access Prometheus at: http://localhost:9090

Features:

Real-time metric visualization
Query interface for custom metrics
Target status monitoring
Alert configuration
Available Metrics
API Metrics (via Flask-Prometheus):

promql

# Request rate
rate(http_requests_total[1m])

# Request duration
histogram_quantile(0.95, http_request_duration_seconds_bucket)

# Error count
increase(http_requests_total{status=~"5.."}[5m])
Query Examples
In Prometheus Query box:

promql

# Check API is up
up{job="api"}

# Request latency
rate(http_request_duration_seconds_sum[1m]) / rate(http_request_duration_seconds_count[1m])

# Success rate
sum(rate(http_requests_total{status=~"2.."}[5m])) / sum(rate(http_requests_total[5m]))
🧠 Task Types & Examples
Calculate Operations
Sum: Add all numbers

JSON

{"task_type": "calculate", "payload": {"numbers": [1,2,3], "operation": "sum"}}
// Result: 6
Product: Multiply all numbers

JSON

{"task_type": "calculate", "payload": {"numbers": [2,3,4], "operation": "product"}}
// Result: 24
Average: Calculate mean

JSON

{"task_type": "calculate", "payload": {"numbers": [10,20,30], "operation": "average"}}
// Result: 20
Transform Operations
Uppercase: Convert to uppercase

JSON

{"task_type": "transform", "payload": {"data": "hello", "operation": "uppercase"}}
// Result: "HELLO"
Lowercase: Convert to lowercase

JSON

{"task_type": "transform", "payload": {"data": "HELLO", "operation": "lowercase"}}
// Result: "hello"
Reverse: Reverse string

JSON

{"task_type": "transform", "payload": {"data": "hello", "operation": "reverse"}}
// Result: "olleh"
Wordcount: Count words

JSON

{"task_type": "transform", "payload": {"data": "hello world test", "operation": "wordcount"}}
// Result: 3
Aggregate Operations
Count & Unique:

JSON

{"task_type": "aggregate", "payload": {"items": ["a", "b", "a", "c"]}}
// Result: {"count": 4, "unique": 3, "sample": ["a", "b", "a"]}
📊 Monitoring & Debugging
View Container Logs
Bash

# All services
docker compose logs

# Specific service
docker compose logs nginx
docker compose logs api
docker compose logs worker
docker compose logs postgres
docker compose logs redis
docker compose logs prometheus

# Follow logs in real-time
docker compose logs -f

# Last 50 lines
docker compose logs --tail=50
Check Container Status
Bash

# List all containers
docker compose ps

# Detailed info
docker compose ps -a

# Inspect container
docker inspect taskqueue-api
Access Databases
PostgreSQL:

Bash

docker compose exec postgres psql -U postgres -d taskqueue

# Useful commands:
# \dt                      - List tables
# SELECT * FROM tasks;     - View all tasks
# \q                       - Exit
Redis:

Bash

docker compose exec redis redis-cli

# Useful commands:
# PING                     - Test connection
# KEYS *                   - List all keys
# LLEN task_queue          - Queue size
# QUIT                     - Exit
🛑 Stopping & Cleanup
Stop Services (Keep Data)
Bash

docker compose stop

# Resume later
docker compose start
Remove Services (Delete Data)
Bash

# Remove containers only
docker compose down

# Remove everything including volumes
docker compose down -v

# Remove everything + unused images
docker compose down -v --remove-orphans
📈 Scaling
Scale Worker Instances
Bash

# Scale to 5 workers
docker compose up -d --scale worker=5

# Check updated status
docker compose ps

# Scale back to 3
docker compose up -d --scale worker=3
🔒 Security Features
✅ Non-root Containers - All services run as non-root users
✅ Security Headers - Nginx includes HSTS, CSP, X-Frame-Options
✅ Secret Management - Secrets stored in .env, not hardcoded
✅ Network Isolation - Services on isolated Docker network
✅ Health Checks - Automatic restart on failure
✅ Graceful Shutdown - Proper signal handling

🚀 Production Deployment
Recommended Enhancements
SSL/TLS - Add HTTPS certificates
Database Backup - Implement backup strategy
Log Aggregation - ELK stack or similar
Authentication - API key or JWT tokens
Rate Limiting - Per-user/IP limits
Database Replication - PostgreSQL streaming
Container Registry - Push to Docker Hub/ECR
Kubernetes - Deploy to K8s for orchestration
🔄 CI/CD Pipeline
GitHub Actions
Pipeline runs automatically on every push:

✅ Code quality checks
✅ Unit tests
✅ Integration tests
✅ Docker image building
✅ Security scanning

View Pipeline: https://github.com/quidditchseeker666/zeotap-sre-assignment/actions

📚 Technology Stack
Component	Technology	Version
Container Platform	Docker	24.0+
Orchestration	Docker Compose	2.0+
API Framework	Flask	3.0.0
Application Server	Gunicorn	21.2.0
Reverse Proxy	Nginx	1.25-alpine
Message Queue	Redis	7-alpine
Database	PostgreSQL	16-alpine
Monitoring	Prometheus	latest
Language	Python	3.11
🐛 Troubleshooting
Issue: Container Won't Start
Solution:

Bash

# Check logs
docker compose logs <service_name>

# Rebuild
docker compose build --no-cache <service_name>

# Try again
docker compose up -d <service_name>
Issue: Port Already in Use
Solution:

Bash

# Find what's using port
sudo lsof -i :8080

# Kill process or change port in docker-compose.yml
Issue: Database Connection Failed
Solution:

Bash

# Check PostgreSQL health
docker compose ps postgres

# Restart PostgreSQL
docker compose restart postgres

# Wait and check again
sleep 10
docker compose ps postgres
Issue: Tasks Not Processing
Solution:

Bash

# Check workers are running
docker compose ps worker

# Check worker logs
docker compose logs worker

# Check Redis connection
docker compose exec redis redis-cli ping
Issue: Prometheus Not Collecting Metrics
Solution:

Bash

# Check Prometheus is running
docker compose ps prometheus

# Check targets
curl http://localhost:9090/api/v1/targets

# Check Prometheus logs
docker compose logs prometheus
📝 Implementation Notes
Task Processing Flow
text

1. Client submits task via POST /api/tasks
   ↓
2. API validates and stores in PostgreSQL
   ↓
3. API adds task to Redis queue
   ↓
4. Worker picks up task from queue (FIFO)
   ↓
5. Worker processes based on task_type
   ↓
6. Worker updates status in PostgreSQL
   ↓
7. Client queries GET /api/tasks/<id> for result
Failure Handling
Failure	Handling
Worker Crash	Docker auto-restarts
Task Error	Logged, status = completed with error
Database Down	Health check fails, Nginx returns 503
Redis Down	New tasks fail with 503 error
📞 Support & Contact
Author: Neelakandan K S
Email: neelakandanks2001@gmail.com
GitHub: https://github.com/quidditchseeker666/zeotap-sre-assignment
Phone: +91-7012048370

✅ Checklist for Verification
 Application runs without errors
 All services are healthy
 Health endpoint returns healthy status
 Task submission works
 Task processing works
 Task status query works
 GitHub repository created
 Documentation complete
 Prometheus monitoring active
 CI/CD pipeline configured
🎓 Learning Outcomes
This project demonstrates:

✅ Docker containerization best practices
✅ Service orchestration with Docker Compose
✅ Distributed systems architecture
✅ Asynchronous task processing
✅ Database design and persistence
✅ API design and REST principles
✅ Load balancing and reverse proxying
✅ Health monitoring and observability
✅ Security in containers and applications
✅ DevOps and SRE best practices
✅ CI/CD automation
✅ Prometheus metrics collection

📄 License
This project was created as part of Zeotap's SRE/DevOps internship assignment.

🙏 Acknowledgments
Built with:

Flask documentation
Docker best practices guide
Nginx configuration examples
PostgreSQL reliability features
Redis queuing patterns
Prometheus monitoring guide
Last Updated: May 5, 2026
Version: 1.0.0
Status: Production Ready ✅

text


---

# ✅ SAVE THIS NOW

Save with `Ctrl + S`

---

# 📋 What This README Includes

✅ Project overview  
✅ System architecture diagram  
✅ Installation instructions  
✅ All API endpoints with examples  
✅ Task type examples  
✅ Testing procedures  
✅ Monitoring guide  
✅ Troubleshooting section  
✅ Scaling instructions  
✅ Security features  
✅ Technology stack  
✅ Production recommendations  
✅ CI/CD info  

---

# 🎯 NEXT STEP

After pasting this README:

```bash
# Commit the complete README
git add README.md
git commit -m "docs: Add comprehensive README with complete documentation"
git push origin main
