from backend.agents.graph import build_graph


def test_minimal_graph_execution():
    """
    Verify LangGraph orchestration skeleton executes successfully.
    """

    graph = build_graph()

    initial_state = {
        "project_id": 1,
        "current_draft_id": 1,
        "extracted_text": "Project Wright test draft.",
        "active_agent": "",
        "pipeline_status": "pending",
        "retry_count": 0,
        "events": [],
    }

    result = graph.invoke(initial_state)

    assert result["pipeline_status"] == "completed"

    assert result["active_agent"] == "placeholder"

    assert len(result["events"]) == 2

    assert result["events"][0]["event"] == "agent_started"

    assert result["events"][1]["event"] == "agent_completed"
