# ⚙️ Backend API Service (FastAPI)

## 📌 Use Case
The **Backend Service** is the **control-plane API** of the VoiceCare AI system.  
It is responsible for:
- Exposing REST APIs for authentication, health checks, and task creation.  
- Publishing tasks to **Google Pub/Sub** for the Worker.  
- Generating **LiveKit tokens** for participants.  
- Notifying workers to join LiveKit rooms.  

Runs on **FastAPI**, deployed on **Cloud Run**, and publishes events to Pub/Sub.

---

## ⚙️ Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
2. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

   Default URL: http://localhost:8080

3. Health check:
   ```bash
   curl http://localhost:8080/health

## 🐳 Running with Docker

1. Build the image:
   ```bash
   docker build -t backend-service .
2. Run the container:
   ```bash
   docker run -p 8080:8080 backend-service
   Accessible at: http://localhost:8080


## 🔄 Synchronous vs Asynchronous

### ✅ Synchronous
- Health check (`/health`)  
- LiveKit token generation (`/api/livekit-token`)  

### ⚡ Asynchronous
- Task publishing (`/api/tasks`)  
- Notifying worker to join LiveKit (`/api/start-room`)  
- Uses **Pub/Sub** to decouple workloads  

### ⚠️ Limitations
- Heavy/long-running tasks must be offloaded to workers  
- Pub/Sub publish failures may trigger retries (handled via DLQ)  

