# 🤖 Worker Service (Python + FastAPI)

## 📌 Use Case
The **Worker Service** is an **event-driven microservice** that processes asynchronous tasks.  
It is responsible for:
- Consuming messages from **Google Pub/Sub** (pushed from the Backend).  
- Joining **LiveKit rooms** as an AI participant.  
- Processing audio/video streams and simulating AI responses.  
- Writing results back to databases (e.g., Cloud SQL, MongoDB).  

Runs on **FastAPI**, deployed on **Cloud Run**, and scales dynamically with Pub/Sub load.

---

## ⚙️ Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt

2. Run the service:
   ```bash
   uvicorn worker:app --host 0.0.0.0 --port 8080 --reload
   Default URL: http://localhost:8080
## 🐳 Running with Docker
1. Build the image:
   ```bash
   docker build -t worker-service .
2. Run the container:
   ```bash
   docker run -p 8080:8080 worker-service
   Accessible at: http://localhost:8080


## 🔄 Synchronous vs Asynchronous

### ✅ Synchronous
- Health endpoint (basic FastAPI `/health`, if extended).  

### ⚡ Asynchronous
- Consumes **Pub/Sub messages** (pushed by Backend).  
- Joins **LiveKit rooms** for real-time audio/video interaction.  
- Simulates AI responses and pushes them back into the room or database.  

### ⚠️ Limitations
- Worker only processes tasks provided via Pub/Sub — no direct synchronous API.  
- Requires reliable Pub/Sub delivery; misconfigured subscriptions may drop messages.  
- Long-lived LiveKit sessions may need autoscaling tuning.  


