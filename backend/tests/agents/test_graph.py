import pytest

from backend.agents.graph import graph


@pytest.mark.asyncio
async def test_graph_execution():
    """
    Validates minimal LangGraph orchestration execution.
    """

    initial_state = {
        "project_id": 1,
        "current_draft_id": 1,
        "extracted_text": "Hello Project Wright",
        "active_agent": "",
        "pipeline_status": "running",
        "retry_count": 0,
        "events": [],
    }

    result = await graph.ainvoke(initial_state)

    assert result["active_agent"] == "placeholder"

    assert result["pipeline_status"] == "completed"

    assert len(result["events"]) == 3

    assert result["events"][0]["event"] == "placeholder_agent_started"

    assert result["events"][1]["event"] == "placeholder_agent_completed"

    assert result["events"][2]["event"] == "pipeline_completed"
