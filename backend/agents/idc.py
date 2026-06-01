# backend/agents/idc.py

from backend.agents.events import create_event
from backend.agents.state import ProjectState


async def idc_node(state: ProjectState) -> ProjectState:
    """
    First real IDC agent.

    Deterministic implementation for Day 7.
    No LLM integration yet.
    """

    state["active_agent"] = "idc"
    state["pipeline_status"] = "running"

    draft_text = state["extracted_text"]

    word_count = len(draft_text.split())

    state["events"].append(
        create_event(
            event="idc_started",
            project_id=state["project_id"],
            agent="idc",
            status="running",
        )
    )

    state["idc_output"] = {
        "summary": draft_text[:500],
        "word_count": word_count,
        "status": "analyzed",
    }

    state["events"].append(
        create_event(
            event="idc_completed",
            project_id=state["project_id"],
            agent="idc",
            status="completed",
            metadata={
                "word_count": word_count,
            },
        )
    )

    return state
