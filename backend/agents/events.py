from datetime import datetime, timezone


def create_event(
    *,
    event: str,
    project_id: int,
    agent: str,
    status: str,
    metadata: dict | None = None,
) -> dict:
    """
    Standardized orchestration event payload.
    """

    return {
        "event": event,
        "project_id": project_id,
        "agent": agent,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    }
