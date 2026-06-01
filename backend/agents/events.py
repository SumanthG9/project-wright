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
    Creates a standardized orchestration event payload.
    """

    return {
        "event": event,
        "project_id": project_id,
        "agent": agent,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    }


WORKFLOW_PAUSED = "workflow_paused"
WAITING_FOR_APPROVAL = "waiting_for_approval"
WORKFLOW_RESUMED = "workflow_resumed"
APPROVAL_RECEIVED = "approval_received"
APPROVAL_REJECTED = "approval_rejected"
PIPELINE_COMPLETED = "pipeline_completed"
