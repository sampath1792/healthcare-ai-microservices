# 🌐 Frontend Service (React + Nginx)

## 📌 Use Case
The **Frontend Service** provides the **user interface** for the VoiceCare AI application.  
It allows users to:
- Interact with the AI assistant via web UI.  
- Start/join LiveKit rooms.  
- Visualize transcripts or AI responses.  

The app is bundled with **React**, built with Node.js, and served via **Nginx**.  
It communicates with the **Backend API** securely over HTTPS.

---

## ⚙️ Running Locally

1. Install dependencies:
   ```bash
   npm install
2. Run the dev server:
   ```bash
   npm start
   Default URL: http://localhost:3000
## 🐳 Running with Docker
1. Build the image:
   ```bash
   docker build -t frontend-service .
2. Run the container:
   ```bash
   docker run -p 3000:80 frontend-service
   Accessible at: http://localhost:3000
## 🔄 Synchronous vs Asynchronous

### ✅ Synchronous
- Direct calls to the backend API (login, token requests, fetching data).  

### ⚡ Asynchronous
- For AI tasks (e.g., transcription or NLP), the backend publishes jobs to **Pub/Sub**, the worker processes them, and the frontend fetches results later (polling or websockets).  

### ⚠️ Limitations
- Async results may take a few seconds to appear in the UI.  
- Requires retry/polling logic for long-running tasks.  
