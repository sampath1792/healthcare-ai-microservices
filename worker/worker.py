'''

This is the sample code added to demonstrate the proper folder structure

'''

import os
import json
import asyncio
from fastapi import FastAPI, Request, HTTPException
from google.cloud import secretmanager
from livekit import api, agents

app = FastAPI(title="voicecare-worker")

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
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://your-livekit-server")

# Securely fetch secrets from Secret Manager
LIVEKIT_API_KEY = get_secret("livekit-api-key", PROJECT_ID)
LIVEKIT_API_SECRET = get_secret("livekit-api-secret", PROJECT_ID)

# --------------------------------------------------
# LiveKit API client
# --------------------------------------------------
lk_client = api.LiveKitAPI(
    LIVEKIT_API_KEY,
    LIVEKIT_API_SECRET,
    LIVEKIT_URL.replace("wss://", "https://")  # mgmt API uses HTTPS
)

# --------------------------------------------------
# Worker functions
# --------------------------------------------------
async def join_livekit_room(room_name: str, identity: str = "ai-worker"):
    """Worker joins a LiveKit room as an AI participant."""
    print(f"[Worker] Joining LiveKit room: {room_name} as {identity}")
    token = lk_client.create_token(
        room=room_name,
        identity=identity,
        can_publish=True,
        can_subscribe=True,
        ttl=1800
    )

    async with agents.Room(LIVEKIT_URL, token) as room:
        print(f"[Worker] Connected to room: {room_name}")

        @room.on("track_subscribed")
        async def handle_track(track):
            print(f"[Worker] Subscribed to track: {track.sid}")
            # TODO: process audio/video streams here
            print(f"[Worker] Received audio/video track")

        await room.run()  # keep connection alive

async def send_ai_response(room_name: str, user_id: str, text: str):
    """Simulates sending AI response back into the LiveKit room."""
    print(f"[Worker] Generating AI response for {user_id} in {room_name}")
    await asyncio.sleep(1)
    print(f"[Worker] Responded: {text.upper()}")

# --------------------------------------------------
# Pub/Sub push endpoint
# --------------------------------------------------
@app.post("/pubsub/push")
async def pubsub_push(request: Request):
    """
    Cloud Run endpoint for Pub/Sub push subscription.
    Pub/Sub sends {"message": {"data": "...base64..."}}
    """
    envelope = await request.json()
    if not envelope or "message" not in envelope:
        raise HTTPException(status_code=400, detail="Invalid Pub/Sub message format")

    pubsub_message = envelope["message"]

    # Decode message data
    data = {}
    if "data" in pubsub_message:
        payload = base64_decode(pubsub_message["data"])
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            print("[Worker] Could not decode Pub/Sub message as JSON")

    print(f"[Worker] Received task: {data}")

    # Handle tasks
    if data.get("task") == "join_room":
        await join_livekit_room(data["room"])

    elif data.get("task") == "ai_response":
        await send_ai_response(data["room"], data["user_id"], data["text"])

    else:
        print(f"[Worker] Unknown task: {data}")

    # Always return 200 for Pub/Sub ACK
    return {"status": "ok"}

# --------------------------------------------------
# Utils
# --------------------------------------------------
def base64_decode(data: str) -> str:
    import base64
    return base64.b64decode(data).decode("utf-8")
