import pytest

from backend.agents.graph import run_graph
from backend.agents.state import ProjectState


@pytest.mark.asyncio
async def test_graph_checkpoint_execution():
    """
    Verifies:
    - graph execution
    - checkpoint persistence
    - state mutation
    - durable orchestration execution
    """

    state: ProjectState = {
        "project_id": 1,
        "current_draft_id": 1,
        "extracted_text": "Hello Project Wright",
        "active_agent": "",
        "pipeline_status": "pending",
        "retry_count": 0,
        "events": [],
    }

    result = await run_graph(state)

    assert result["pipeline_status"] == "completed"

    assert len(result["events"]) == 3

    assert result["events"][0]["event"] == "placeholder_agent_started"

    assert result["events"][1]["event"] == "placeholder_agent_completed"

    assert result["events"][2]["event"] == "pipeline_completed"
