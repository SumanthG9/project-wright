from datetime import datetime, timezone
from typing import Any


def create_event(
    event: str,
    project_id: int,
    agent: str,
    status: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create a standardized orchestration event payload.
    """

    return {
        "event": event,
        "project_id": project_id,
        "agent": agent,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    }
