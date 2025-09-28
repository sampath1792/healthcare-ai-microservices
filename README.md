# 🎙️ VoiceCare – Cloud-Native AI Application

This project demonstrates a **production-grade cloud-native application** built on **Google Cloud Platform (GCP)**.  
It highlights **modern DevOps practices, microservice architecture, secure networking, and real-time AI processing**.

The system is designed to handle **real-time voice conversations** where users interact with an AI assistant through **LiveKit (audio/video infra)**.  
It supports **secure APIs, async job processing, database operations, and observability** – all deployed with **scalable, cost-efficient, and secure GCP services**.

---

## 📐 Architecture

![Architecture Diagram](./image.png)

---

## 🔑 Components & Responsibilities

### **Frontend Service (React, served via Cloud Run & CDN)**
- Provides the **user interface** for web/mobile users.  
- Deployed on **Cloud Run**, optionally accelerated via **Cloud CDN** for static assets.  
- Sends API requests securely via **HTTPS (API Gateway + Load Balancer)**.  

---

### **Backend API Service (FastAPI, Cloud Run)**
- Core **control-plane** API.  
- Responsible for:
  - **User authentication & session management** (JWT, API Keys).  
  - **Publishing async jobs** to Pub/Sub.  
  - **Integrating with databases** (Postgres & MongoDB).  
  - **Proxying requests to external APIs (e.g., LiveKit, AI/ML APIs)**.  
- Always kept warm (`min=1 instance`) to ensure low-latency API responses.  

---

### **AI Worker Service (Python, Pub/Sub Consumer)**
- **Event-driven worker** for async jobs.  
- Scales dynamically based on Pub/Sub load (`min=0, max=30`).  
- Responsibilities:
  - Consumes Pub/Sub tasks.  
  - Connects to **LiveKit rooms** to simulate AI audio/video responses.  
  - Calls external **AI/ML APIs** for inference.  
  - Writes session results back to **Cloud SQL / MongoDB**.  

---

### **Pub/Sub (Messaging Layer)**
- Decouples backend API and workers.  
- Ensures reliable async processing with:
  - **Dead Letter Queues (DLQ)** for failed jobs.  
  - **Idempotent workers** for safe retries.  
  - **Ack & retry policies** for resiliency.  

---

### **Databases**
- **Cloud SQL (Postgres)**  
  - Used for structured data (users, sessions, transactions).  
  - Private IP only, TLS enforced.  

- **MongoDB Atlas (via VPC Peering)**  
  - Used for unstructured/JSON-like data (AI session logs, transcripts).  
  - Access restricted by VPC peering and TLS.  

---

### **Secret Manager**
- Securely stores **API keys, DB credentials, and tokens**.  
- Injected at runtime into services.  
- Avoids hardcoding sensitive values.  

---

### **External APIs**
- **LiveKit**: Real-time audio/video infra for AI conversations.  
- **AI/ML APIs**: Speech-to-text (STT), text-to-speech (TTS), NLP models.  
- Accessed via secure **outbound traffic through Cloud NAT**.  

---

### **Networking & Security**
- **VPC with private & public subnets**  
  - Public Subnet: Load Balancer, API Gateway.  
  - Private Subnet: Backend, Workers, Databases.  

- **Firewall Rules**  
  - Only **HTTPS (443)** exposed via LB.  
  - No direct DB or worker public exposure.  
  - Outbound traffic allowed only via **Cloud NAT**.  

- **Cloud Armor**  
  - Web Application Firewall (WAF).  
  - Protects against DDoS, SQLi, XSS.  
  - Enforces rate limiting.  

- **IAM Service Accounts**  
  - Each service runs with least-privilege IAM roles.  
  - Example:  
    - `sa-backend` → Pub/Sub publisher + Secret Manager access.  
    - `sa-worker` → Pub/Sub subscriber + Secret Manager access.  

---

### **Observability**
- **Cloud Monitoring & Logging**  
  - Collects logs, metrics, and traces.  
  - Helps in troubleshooting, scaling analysis, and audits.  

---

## ⚙️ CI/CD Workflow

- **GitHub Actions** handles build & deploy:
  1. Run tests on each service.  
  2. Build Docker images.  
  3. Push images to **Artifact Registry**.  
  4. Deploy services to **Cloud Run** via **Workload Identity Federation** (no long-lived secrets).  

---

## 🚀 Scaling & Performance

- **Frontend**  
  - Scales between 0 → 10 instances.  

- **Backend API**  
  - Scales between 1 → 50 instances.  
  - Concurrency set for low-latency APIs.  

- **AI Worker**  
  - Scales 0 → 30 based on Pub/Sub load.  

- **Load Testing**  
  - Verified with **Locust & k6**.  
  - Achieves **1000 RPS sustained** with **<200ms latency**.  

---

## 🔐 Security Best Practices

- **All secrets in Secret Manager** (no plaintext configs).  
- **TLS enforced** across all services.  
- **Private IP access only** for databases.  
- **Rate limiting + WAF** via Cloud Armor.  
- **Separate IAM identities per service** → strong least-privilege model.  

---

## ✅ Key Benefits of This Architecture

- **Scalable** → auto-scales frontend, backend, workers.  
- **Secure** → TLS everywhere, WAF, IAM-based access, private networking.  
- **Cost-efficient** → serverless Cloud Run + scale-to-zero workers.  
- **Reliable** → Pub/Sub with DLQ, retries, and idempotency.  
- **Developer-friendly** → CI/CD with GitHub Actions, no manual deployments.  

---

## 📂 Repository Layout

