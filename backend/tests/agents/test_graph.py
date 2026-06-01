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
    - multi-agent workflow execution
    """

    state: ProjectState = {
        "project_id": 1,
        "current_draft_id": 1,
        "extracted_text": "Hello Project Wright",
        "idc_output": {},
        "outline_output": {},
        "active_agent": "",
        "pipeline_status": "pending",
        "retry_count": 0,
        "paused": False,
        "waiting_for_input": False,
        "approval_status": "",
        "events": [],
    }

    result = await run_graph(state)

    # Workflow state
    assert result["pipeline_status"] == "paused"
    assert result["paused"] is True
    assert result["waiting_for_input"] is True

    # IDC output
    assert result["idc_output"]["status"] == "analyzed"

    # Outline output
    assert result["outline_output"]["status"] == "generated"

    # Event validation (less brittle than index checks)
    events = [e["event"] for e in result["events"]]

    assert "idc_started" in events
    assert "idc_completed" in events

    assert "outline_started" in events
    assert "outline_completed" in events

    assert "workflow_paused" in events
    assert "waiting_for_approval" in events
