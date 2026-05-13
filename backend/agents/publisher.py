import json

import redis.asyncio as redis

from backend.core.config import settings


def get_redis_client():
    """
    Create a Redis client bound to the current active event loop.
    """

    return redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )


async def publish_event(project_id: int, event: dict) -> None:
    """
    Publish orchestration events to a project-scoped Redis channel.
    """

    redis_client = get_redis_client()

    channel = f"pipeline:{project_id}"

    await redis_client.publish(
        channel,
        json.dumps(event),
    )

    await redis_client.close()
