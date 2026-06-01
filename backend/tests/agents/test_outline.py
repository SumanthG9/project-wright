import pytest

from backend.agents.outline import outline_node


@pytest.mark.asyncio
async def test_outline_execution():
    state = {
        "project_id": 1,
        "current_draft_id": 1,
        "extracted_text": "Hello Project Wright",
        "idc_output": {
            "summary": "Hello Project Wright",
            "word_count": 3,
            "status": "analyzed",
        },
        "outline_output": {},
        "active_agent": "",
        "pipeline_status": "pending",
        "retry_count": 0,
        "paused": False,
        "waiting_for_input": False,
        "approval_status": "",
        "events": [],
    }

    result = await outline_node(state)

    assert result["outline_output"]["status"] == "generated"
    assert len(result["outline_output"]["sections"]) > 0

    events = [e["event"] for e in result["events"]]

    assert "outline_started" in events
    assert "outline_completed" in events
