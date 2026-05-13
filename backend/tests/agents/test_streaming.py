import asyncio
import json

import pytest
import redis.asyncio as redis

from backend.agents.publisher import publish_event
from backend.core.config import settings


@pytest.mark.asyncio
async def test_redis_pubsub_streaming():
    """
    Validates Redis pub/sub event propagation.
    """

    redis_client = redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )

    pubsub = redis_client.pubsub()

    channel = "pipeline:999"

    await pubsub.subscribe(channel)

    test_event = {
        "event": "test_event",
        "project_id": 999,
        "agent": "test",
        "status": "running",
    }

    await asyncio.sleep(0.1)

    await publish_event(
        project_id=999,
        event=test_event,
    )

    async for message in pubsub.listen():

        if message["type"] != "message":
            continue

        payload = json.loads(message["data"])

        assert payload["event"] == "test_event"
        assert payload["project_id"] == 999

        break

    await pubsub.unsubscribe(channel)
    await pubsub.close()
