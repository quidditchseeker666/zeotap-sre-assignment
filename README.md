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