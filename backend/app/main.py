
'''

This is the sample code added to demonstrate the proper folder structure

'''



from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from google.cloud import pubsub_v1
from livekit import api as lk_api
import os
import json

app = FastAPI(title="voicecare-backend")

# Environment variables
PROJECT_ID = os.getenv("PROJECT_ID", "your-gcp-project-id")
TOPIC_ID = os.getenv("PUBSUB_TOPIC", "voicecare-tasks")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "https://your-livekit-server")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# Pub/Sub publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

# LiveKit API client
lk_client = lk_api.LiveKitAPI(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL)


@app.get("/health")
def health():
    return {"status": "ok"}


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

    task = {"task": "join_room", "room": req.room}
    data = json.dumps(task).encode("utf-8")
    future = publisher.publish(topic_path, data, source="backend")
    message_id = future.result(timeout=10)
    return {"message": "worker-notified", "room": req.room, "message_id": message_id}
