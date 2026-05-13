import asyncio
import json

import redis.asyncio as redis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.core.config import settings

router = APIRouter()


def get_redis_client():
    return redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )


@router.websocket("/projects/{project_id}")
async def project_ws(
    websocket: WebSocket,
    project_id: int,
):
    """
    Streams orchestration events for a project.
    """

    await websocket.accept()

    print(f"WebSocket connected for project {project_id}")

    redis_client = get_redis_client()

    pubsub = redis_client.pubsub()

    channel = f"pipeline:{project_id}"

    await pubsub.subscribe(channel)

    try:
        while True:

            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1.0,
            )

            if message:

                payload = json.loads(message["data"])

                await websocket.send_json(payload)

            await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for project {project_id}")

    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
        await redis_client.aclose()
