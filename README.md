# 🎙️ VoiceCare – Cloud-Native AI Application

This repository demonstrates a **cloud-native healthcare AI application** built using **Google Cloud Platform (GCP)**.  

It highlights **modern DevOps practices**, **secure microservice architecture**, **real-time AI audio processing**, and **scalable CI/CD workflows**.

The system enables **real-time voice conversations** between users and an AI assistant using **LiveKit (audio/video infra)**, while ensuring **security, observability, and cost efficiency**.

---

## 📐 Architecture

![Architecture Diagram](./image.png)

---

## 🔑 Core Components

### **Frontend Service (React, Cloud Run, CDN)**
- Provides the **web/mobile UI** for users.  
- Containerized React app deployed on **Cloud Run**.  
- Optionally accelerated via **Cloud CDN** for static assets.  
- Communicates securely through **HTTPS → Load Balancer → API Gateway**.  

---

### **Backend API Service (FastAPI, Cloud Run)**
- Implements the **control-plane APIs**.  
- Responsibilities:
  - User authentication & **JWT / API Key session management**.  
  - Publishes async jobs to **Pub/Sub**.  
  - Handles **DB operations** with Postgres (Cloud SQL) and MongoDB Atlas.  
  - Proxies requests to **external APIs** (LiveKit, AI/ML APIs).  
- **Always-on** with min=1 instance for low-latency response.  
- Deployed with **least-privilege service account** (`sa-backend`).  

---

### **AI Worker Service (Python, Pub/Sub Consumer, Cloud Run)**
- Implements the **data-plane processing**.  
- Event-driven worker triggered by Pub/Sub.  
- Responsibilities:
  - Consumes tasks from Pub/Sub.  
  - Connects to **LiveKit rooms** for real-time audio/video responses.  
  - Calls **AI/ML APIs** (STT, NLP, TTS).  
  - Writes results back to **Cloud SQL & MongoDB**.  
- Scales dynamically (`min=0, max=30`).  
- Uses dedicated **service account** (`sa-worker`).  

---

### **Pub/Sub (Messaging Layer)**
- Decouples backend and workers.  
- Provides async reliability with:
  - **Dead Letter Queue (DLQ)** for failed tasks.  
  - **Idempotent workers** to ensure safe retries.  
  - **Ack & retry policies** for resiliency.  

---

### **Databases**
- **Cloud SQL (Postgres)**  
  - Stores structured data (users, sessions, transactions).  
  - **Private IP only, TLS enforced**.  
  - Access limited to backend/worker service accounts.  

- **MongoDB Atlas (via VPC Peering)**  
  - Stores unstructured JSON-like data (AI transcripts, logs).  
  - **VPC Peering + TLS enforced**.  

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

### **VPC Setup**
- **voicecare-vpc (10.10.0.0/16)**  
  - **Public Subnet (10.10.1.0/24):** Load Balancer, API Gateway, optional CDN.  
  - **Private Subnet (10.10.2.0/24):** Backend, Worker, Databases.  

### **Firewall Rules**
- Only **HTTPS (443)** exposed (via Load Balancer).  
- No direct public DB/worker exposure.  
- Outbound internet only via **Cloud NAT**.  
- Internal communication restricted to VPC ranges.  

### **Cloud Armor (WAF & Rate Limiting)**
- TLS termination + WAF rules for SQLi/XSS protection.  
- Rate limiting against brute-force/DDoS.  

### **IAM Service Accounts**
- **sa-backend** → Pub/Sub publisher + Secret Manager reader + DB access.  
- **sa-worker** → Pub/Sub subscriber + Secret Manager reader + DB write.  
- **sa-ci-cd** → GitHub Actions deploy via Workload Identity Federation.  
- **Principle:** Least-privilege access, rotated automatically.  

---

## 📊 Observability
- **Cloud Monitoring & Logging (Ops Suite)**  
  - Collects logs, traces, and metrics.  
  - Monitors latency, error rates, and Pub/Sub backlog.  
  - Alerts on anomalies (e.g., 5xx errors, high latency).  

---

## ⚙️ CI/CD Workflow

- **GitHub Actions** automates builds and deployments:  
  1. Run linting & unit tests.  
  2. Build multi-stage Docker images.  
  3. Push images to **Artifact Registry**.  
  4. Deploy to **Cloud Run** via **Workload Identity Federation** (no static secrets).  

---

## 🚀 Scaling & Load Testing

- **Frontend (Cloud Run)** → 0 → 10 instances.  
- **Backend API (Cloud Run)** → 1 → 50 instances.  
- **AI Worker (Cloud Run)** → 0 → 30 instances.  
- **Load testing setup**: Locust & k6.  
  - Sustains **1000 RPS** with **<200ms latency**.  

---

## 🔐 Security Best Practices

- Secrets stored in **Secret Manager** (no plaintext in code).  
- **TLS enforced everywhere** (internal + external).  
- **Private IP only** for DB access.  
- **Cloud Armor (WAF + Rate limiting)**.  
- **Service accounts with least-privilege IAM roles**.  
- **VPC peering for MongoDB Atlas**.  
- **CI/CD with Workload Identity Federation** (no long-lived credentials).  

---

## ✅ Benefits of This Architecture

- **Scalable** → auto-scales workers, backend, frontend.  
- **Secure** → TLS, IAM, WAF, private networking.  
- **Reliable** → Pub/Sub with retries & DLQ.  
- **Cost-efficient** → serverless Cloud Run + scale-to-zero workers.  
- **Developer-friendly** → GitHub Actions CI/CD, clear repo structure.  

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
