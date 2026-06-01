import pytest

from backend.agents.graph import resume_graph, run_graph


@pytest.mark.asyncio
async def test_hitl_pause_resume():
    state = {
        "project_id": 1,
        "current_draft_id": 1,
        "extracted_text": "test draft",
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

    paused_state = await run_graph(state)

    assert paused_state["pipeline_status"] == "paused"
    assert paused_state["paused"] is True

    resumed_state = await resume_graph(
        paused_state,
        approval="approved",
    )

    assert resumed_state["pipeline_status"] == "completed"
    assert resumed_state["approval_status"] == "approved"
