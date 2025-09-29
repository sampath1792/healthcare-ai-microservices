'''

This is the sample code added to demonstrate the proper folder structure

'''

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from google.cloud import pubsub_v1, secretmanager
from livekit import api as lk_api
import os
import json

app = FastAPI(title="voicecare-backend")

# --------------------------------------------------
# Helper: Fetch secret from Secret Manager
# --------------------------------------------------
def get_secret(secret_id: str, project_id: str = None) -> str:
    """Fetch the latest version of a secret from GCP Secret Manager."""
    project_id = project_id or os.getenv("PROJECT_ID", "your-gcp-project-id")
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("utf-8")

# --------------------------------------------------
# Environment variables / Secrets
# --------------------------------------------------
PROJECT_ID = os.getenv("PROJECT_ID", "your-gcp-project-id")
TOPIC_ID = os.getenv("PUBSUB_TOPIC", "voicecare-tasks")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "https://your-livekit-server")

# Fetch sensitive values from Secret Manager
LIVEKIT_API_KEY = get_secret("livekit-api-key", PROJECT_ID)
LIVEKIT_API_SECRET = get_secret("livekit-api-secret", PROJECT_ID)

# --------------------------------------------------
# Pub/Sub publisher
# --------------------------------------------------
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

# --------------------------------------------------
# LiveKit API client
# --------------------------------------------------
lk_client = lk_api.LiveKitAPI(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL)

# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.get("/health")
def health():
    """Simple health check endpoint."""
    return {"status": "ok"}

# ---------------- Task Publishing -----------------

class Task(BaseModel):
    user_id: str
    text: str

@app.post("/api/tasks")
def create_task(task: Task, authorization: str = Header(None)):
    """Publishes tasks for async processing by the worker."""
    if not authorization:
        raise HTTPException(status_code=401, detail="missing auth")

    try:
        data = json.dumps(task.dict()).encode("utf-8")
        future = publisher.publish(topic_path, data, source="backend")
        message_id = future.result(timeout=10)
        return {"message": "accepted", "task": task, "message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pub/Sub publish failed: {e}")


# ---------------- LiveKit Token -------------------

class TokenRequest(BaseModel):
    room: str
    identity: str

@app.post("/api/livekit-token")
def get_livekit_token(req: TokenRequest, authorization: str = Header(None)):
    """Generates a LiveKit join token for a user or worker."""
    if not authorization:
        raise HTTPException(status_code=401, detail="missing auth")

    try:
        token = lk_client.create_token(
            room=req.room,
            identity=req.identity,
            ttl=3600,  # 1 hour
            can_publish=True,
            can_subscribe=True,
        )
        return {"token": token, "room": req.room, "identity": req.identity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LiveKit token error: {e}")


# ---------------- Start Room ----------------------

class RoomRequest(BaseModel):
    room: str

@app.post("/api/start-room")
def start_room(req: RoomRequest, authorization: str = Header(None)):
    """
    Publishes a message for worker to join a LiveKit room.
    This kicks off the AI assistant in that room.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="missing auth")

    try:
        task = {"task": "join_room", "room": req.room}
        data = json.dumps(task).encode("utf-8")
        future = publisher.publish(topic_path, data, source="backend")
        message_id = future.result(timeout=10)
        return {"message": "worker-notified", "room": req.room, "message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pub/Sub publish failed: {e}")
