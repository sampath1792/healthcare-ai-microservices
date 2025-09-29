# 🛠️ DevOps Overview – VoiceCare AI Application

This document provides an overview of the **DevOps architecture, security practices, CI/CD pipeline, and operations** for the VoiceCare AI project.

It complements the per-service READMEs and the root README by focusing on **infrastructure, deployment, scaling, and security**.

---

## 📐 Infrastructure & Deployment

- **Cloud Provider**: Google Cloud Platform (GCP)  
- **Services Used**:
  - **Cloud Run** → Runs all microservices (frontend, backend, worker).  
  - **Pub/Sub** → Messaging layer for async communication.  
  - **Cloud SQL (Postgres)** → Relational data storage.  
  - **MongoDB Atlas (VPC Peering)** → Unstructured/JSON data storage.  
  - **Secret Manager** → Secure secret storage.  
  - **Cloud Armor** → Web Application Firewall & rate limiting.  
  - **Cloud NAT** → Outbound API access.  
  - **Cloud Monitoring & Logging** → Observability stack.  

- **Deployment Model**:
  - All services containerized with **multi-stage Docker builds**.  
  - Built images pushed to **Artifact Registry**.  
  - Deployed to Cloud Run via **GitHub Actions** + **Workload Identity Federation** (no long-lived secrets).  

---

## 🔑 IAM & Service Accounts

Each service runs with a **dedicated IAM service account** for least-privilege access:

- **sa-backend**
  - Pub/Sub **publisher**  
  - Secret Manager **reader**  
  - Cloud SQL & MongoDB access  

- **sa-worker**
  - Pub/Sub **subscriber**  
  - Secret Manager **reader**  
  - Cloud SQL & MongoDB write  

- **sa-frontend**
  - Minimal access (read-only configs, no DB access)  

- **sa-ci-cd**
  - Used by **GitHub Actions** for deploying Cloud Run services.  
  - Authenticated via **Workload Identity Federation**.  

**Principle**: Each service account only has the roles it strictly needs (least privilege).

---

## 🔒 Networking & Security

### VPC Layout
- **voicecare-vpc (10.10.0.0/16)**  
  - **Public Subnet (10.10.1.0/24)**: Load Balancer, API Gateway.  
  - **Private Subnet (10.10.2.0/24)**: Backend, Worker, Databases.  

### Firewall Rules
- **Ingress**
  - Allow `443 (HTTPS)` only → Load Balancer/API Gateway.  
  - Deny all direct DB access from internet.  
- **Egress**
  - Outbound API calls allowed only through **Cloud NAT**.  
- **Internal**
  - Backend/Worker access databases only via VPC private IPs.  

### Cloud Armor
- Protects public endpoints from:
  - SQL Injection (SQLi).  
  - Cross-Site Scripting (XSS).  
  - DDoS attacks.  
- Implements **rate limiting** for APIs.  

### Secrets
- Managed via **Secret Manager**.  
- Rotated automatically, injected at runtime.  
- No plaintext secrets in source code or CI/CD.  

---

## 🔄 Synchronous vs Asynchronous Tasks

- **Synchronous** (low-latency APIs)
  - Frontend ↔ Backend API (auth, small DB queries).  
  - Direct API calls (short response times).  

- **Asynchronous** (long-running jobs)
  - Backend publishes tasks to **Pub/Sub**.  
  - Worker consumes events → processes AI/ML tasks → stores results.  
  - Resiliency:
    - **Retry/backoff policies**.  
    - **Dead Letter Queue (DLQ)** for failed tasks.  
    - **Idempotency** to prevent duplicate results.  

---

## ⚙️ CI/CD Workflow (GitHub Actions)

Workflow file: `.github/workflows/ci-cd.yml`

### Steps
1. **Lint & Unit Tests** → Validate code quality.  
2. **Build Docker Images** → Multi-stage builds for small, secure images.  
3. **Push to Artifact Registry** → Images stored in GCP Artifact Registry.  
4. **Deploy to Cloud Run** → Using `gcloud run deploy` with Workload Identity Federation.  
5. **Post-deploy checks** → Health checks, smoke tests.  

---

## 📊 Observability

- **Cloud Monitoring**
  - Latency, error rate, Pub/Sub backlog.  
  - Alerts for high error rates (>5%) or high latency (>500ms).  

- **Cloud Logging**
  - Centralized structured logs.  
  - Log-based metrics → alerts for anomalies.  

- **Tracing**
  - Request tracing across services for debugging latency issues.  

---

## 🚀 Scaling & Load Testing

- **Frontend (Cloud Run)** → Scales 0 → 10 instances.  
- **Backend API (Cloud Run)** → Scales 1 → 50 instances.  
- **Worker (Cloud Run)** → Scales 0 → 30 instances.  

- **Load Testing Setup**:
  - **Locust** & **k6** used for benchmarking.  
  - Achieved **1000 RPS sustained** with **<200ms latency** under load.  

---

## ✅ Benefits

- **Security-first** → TLS, IAM least privilege, Secret Manager, WAF.  
- **Scalable & resilient** → Cloud Run autoscaling, Pub/Sub async processing, DLQs.  
- **Cost-efficient** → Serverless scale-to-zero for workers.  
- **Automation** → GitHub Actions CI/CD with no manual deployments.  
- **Observability built-in** → Logs, metrics, alerts, tracing.  

---

## 📘 Related Documentation

- [Root README.md](/README.md) → Full project architecture & overview.  
- [frontend/README.md](../frontend/README.md) → Frontend service details.  
- [backend/README.md](../backend/README.md) → Backend service details.  
- [worker/README.md](../worker/README.md) → Worker service details.  
