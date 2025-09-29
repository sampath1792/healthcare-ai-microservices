# 🎙️ VoiceCare – Cloud-Native AI Application

This repository demonstrates a **cloud-native healthcare AI application** built on **Google Cloud Platform (GCP)**.  

It showcases:
- **Modern DevOps practices**  
- **Secure microservice architecture**  
- **Real-time AI audio/video processing**  
- **Scalable CI/CD workflows**  

The system enables **real-time voice conversations** between users and an AI assistant using **LiveKit (audio/video infra)**, while ensuring **security, observability, and cost efficiency**.

---

## 📐 Architecture

![Architecture Diagram](./image.png)

---

## 🔑 Core Components

### **Frontend Service (React + Nginx, Cloud Run, CDN)**
- Provides the **web/mobile UI** for users.  
- Containerized React app deployed on **Cloud Run**.  
- Optionally accelerated with **Cloud CDN**.  
- Communicates securely through **HTTPS → Load Balancer → API Gateway**.  
- Runs with **least-privilege service account** (`sa-frontend`).  

---

### **Backend API Service (FastAPI, Cloud Run)**
- Implements the **control-plane APIs**.  
- Responsibilities:
  - User authentication & **JWT / API Key session management**.  
  - Publishes async jobs to **Pub/Sub**.  
  - Handles **DB operations** with Postgres (Cloud SQL) and MongoDB Atlas.  
  - Proxies requests to **external APIs** (LiveKit, AI/ML APIs).  
- **Always-on** (min=1 instance) to ensure low-latency responses.  
- Runs with **least-privilege service account** (`sa-backend`).  

---

### **AI Worker Service (Python, Pub/Sub Consumer, Cloud Run)**
- Implements the **data-plane processing**.  
- Event-driven worker triggered by Pub/Sub.  
- Responsibilities:
  - Consumes tasks from Pub/Sub.  
  - Connects to **LiveKit rooms** for real-time audio/video responses.  
  - Calls **AI/ML APIs** (STT, NLP, TTS).  
  - Stores results in **Cloud SQL & MongoDB**.  
- Scales dynamically (`min=0, max=30`).  
- Runs with **least-privilege service account** (`sa-worker`).  

---

### **Pub/Sub (Messaging Layer)**
- Decouples backend and workers.  
- Provides async reliability with:
  - **Dead Letter Queue (DLQ)** for failed tasks.  
  - **Idempotent workers** to prevent duplicate processing.  
  - **Ack & retry policies** for resiliency.  

---

### **Databases**
- **Cloud SQL (Postgres)**  
  - Stores structured data (users, sessions, transactions).  
  - **Private IP only, TLS enforced**.  

- **MongoDB Atlas (via VPC Peering)**  
  - Stores unstructured/JSON-like data (AI transcripts, logs).  
  - Access restricted by **VPC peering + TLS**.  

---

### **Secret Manager**
- Centralized **secrets management** for API keys, DB creds, tokens.  
- Secrets injected securely at runtime → no plaintext configs.  
- Access controlled via **IAM roles** per service account.  

---

### **External APIs**
- **LiveKit** → Real-time audio/video infra.  
- **AI/ML APIs** → Speech-to-Text (STT), NLP, Text-to-Speech (TTS).  
- All outbound traffic goes through **Cloud NAT** for security.  

---

## 🔒 Networking & Security

### **VPC Layout**
- **voicecare-vpc (10.10.0.0/16)**  
  - **Public Subnet (10.10.1.0/24):** Load Balancer, API Gateway, optional CDN.  
  - **Private Subnet (10.10.2.0/24):** Backend, Worker, Databases.  

### **Firewall Rules**
- **Ingress:**  
  - Only allow `443 (HTTPS)` via Load Balancer.  
  - Deny all direct DB/worker access from internet.  

- **Egress:**  
  - Outbound calls only via **Cloud NAT**.  

- **Internal:**  
  - DBs accessible only to backend & worker via VPC private IPs.  

### **Cloud Armor (WAF & Rate Limiting)**
- Protects against SQL Injection (SQLi), XSS, DDoS.  
- Enforces **rate limiting** on public APIs.  

### **IAM Service Accounts**
- **sa-backend** → Pub/Sub publisher + Secret Manager + DB access.  
- **sa-worker** → Pub/Sub subscriber + Secret Manager + DB write.  
- **sa-frontend** → Minimal access (read-only configs).  
- **sa-ci-cd** → GitHub Actions deploy via Workload Identity Federation.  
- **Principle:** Least-privilege access, rotated automatically.  

---

## 🔄 Synchronous vs Asynchronous

### ✅ Synchronous
- Health checks & lightweight API requests.  
- Authentication & token generation.  
- Direct DB reads.  

### ⚡ Asynchronous
- Long-running AI/ML tasks processed by **Worker**.  
- Backend publishes tasks → Pub/Sub → Worker executes → results stored.  

### ⚠️ Limitations
- Async tasks may have delays (seconds).  
- Requires **retry & DLQ** for resiliency.  
- Idempotency must be enforced to avoid duplicates.  

---

## ⚙️ CI/CD Workflow

Workflow file: `.github/workflows/ci-cd.yml`

- **GitHub Actions** automates:
  1. Run linting & unit tests.  
  2. Build multi-stage Docker images.  
  3. Push images to **Artifact Registry**.  
  4. Deploy to **Cloud Run** via **Workload Identity Federation** (no static secrets).  
  5. Run smoke tests after deployment.  

---

## 📊 Observability

- **Cloud Monitoring** → metrics (latency, error rate, Pub/Sub backlog).  
- **Cloud Logging** → centralized structured logs.  
- **Tracing** → request tracing across services.  
- **Alerts** → triggered on >5% errors or >500ms latency.  

---

## 🚀 Scaling & Load Testing

- **Frontend (Cloud Run):** 0 → 10 instances.  
- **Backend API (Cloud Run):** 1 → 50 instances.  
- **Worker (Cloud Run):** 0 → 30 instances.  

### Load Testing
- Tools: **Locust & k6**.  
- Sustains **1000 RPS** with **<200ms latency** under load.  

---

## 🔐 Security Best Practices

- Secrets only in **Secret Manager**.  
- **TLS enforced** across all services.  
- **Private IP only** for DBs.  
- **Cloud Armor WAF + rate limiting**.  
- **Service accounts with least privilege**.  
- **VPC peering** for MongoDB Atlas.  
- **CI/CD with Workload Identity Federation** (no long-lived secrets).  

---

## ✅ Benefits of This Architecture

- **Scalable** → auto-scales workers, backend, frontend.  
- **Secure** → TLS, IAM, WAF, private networking.  
- **Reliable** → Pub/Sub with retries & DLQ.  
- **Cost-efficient** → serverless Cloud Run + scale-to-zero workers.  
- **Developer-friendly** → CI/CD with GitHub Actions, clear repo structure.  

---

## 📂 Repository Layout

.
├── .github/
│ └── workflows/
│ └── ci-cd.yml # CI/CD pipeline
├── README.md # Root documentation (this file)
├── backend/ # FastAPI backend microservice
│ ├── Dockerfile
│ ├── app/
│ │ └── main.py
│ ├── requirements.txt
│ └── tests/
├── frontend/ # React frontend microservice
│ ├── Dockerfile
│ ├── nginx.conf
│ └── package.json
├── worker/ # Python AI worker microservice
│ ├── Dockerfile
│ ├── worker.py
│ └── requirements.txt
└── image.png # Architecture diagram


---

## 📘 Documentation

- Each microservice has a **README** with local & cloud run instructions.  
- Root README (this file) provides **architecture overview, security, CI/CD, and scaling strategy**.  

---

## 🏁 Conclusion

This project delivers a **secure, scalable, cloud-native architecture** for healthcare AI.  
It adheres to **best DevOps practices**, enforces **strict security controls**, and is built for **real-world production workloads**.
