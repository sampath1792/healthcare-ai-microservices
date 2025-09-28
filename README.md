# VoiceCare Cloud-Native Application

This project demonstrates a **3-microservice cloud-native application** deployed on **Google Cloud Run** with full DevOps practices.  
It is designed to show **architecture, CI/CD, scaling, secret management, and security/networking setup** as part of the DevOps assignment.

---

## 📐 Architecture Diagram

![Architecture Diagram](./image.png)

### 🔑 Components

- **Frontend (React + Nginx)**  
  - UI for users to interact with the app.  
  - Served from Cloud Run, optionally fronted by Cloud CDN.  

- **Backend API (FastAPI + Uvicorn)**  
  - Manages tasks, proxies requests to LiveKit, and will manage DB operations (Cloud SQL, MongoDB).  
  - Publishes async tasks to Pub/Sub for workers.  

- **AI Worker (FastAPI, Pub/Sub trigger)**  
  - Event-driven worker consuming Pub/Sub messages.  
  - Joins LiveKit rooms as AI participant, simulates responses, stores session data.  

- **Google Cloud Components**  
  - **Cloud Run**: Deploys all microservices.  
  - **Pub/Sub**: Async task queue between Backend and Worker.  
  - **Cloud SQL (Postgres)**: Relational DB.  
  - **MongoDB Atlas**: NoSQL DB via VPC peering.  
  - **Secret Manager**: Stores API keys, DB credentials.  
  - **API Gateway / HTTPS Load Balancer**: Entry point for frontend and backend.  
  - **Cloud Armor**: WAF for request filtering.  
  - **VPC & Subnets**: Network isolation with firewall rules.  

---

## ⚙️ CI/CD

- **GitHub Actions** runs on every push:
  1. Build and test each service (frontend, backend, worker).
  2. Build Docker images and push to Artifact Registry.
  3. Deploy to Cloud Run with service accounts & workload identity federation.

---

## 🚀 Scaling and Load Testing

- **Frontend**: min=0, max=10 → scales to zero when idle.  
- **Backend**: min=1, max=50, concurrency=80 → always warm for low-latency API.  
- **Worker**: min=0, max=30 → event-driven scaling with Pub/Sub load.  

Load tested with **k6** to verify throughput and latency.

---

## 🔐 Security

- All secrets stored in **Secret Manager**.  
- Each service runs with a **dedicated IAM service account** with least privileges:
  - `sa-frontend` (Cloud Run invocation only).  
  - `sa-backend` (Pub/Sub publisher, Secret Manager).  
  - `sa-worker` (Pub/Sub subscriber, Secret Manager).  
- **VPC firewall rules** restrict DB access to backend/worker only.  
- **Cloud Armor** protects against SQLi/XSS attacks.  

---

## 📂 Repository Structure

