from backend.agents.events import create_event
from backend.agents.state import ProjectState


async def outline_node(state: ProjectState) -> ProjectState:
    """
    First downstream agent.

    Consumes IDC output and generates a
    deterministic outline artifact.
    """

    state["active_agent"] = "outline"
    state["pipeline_status"] = "running"

    state["events"].append(
        create_event(
            event="outline_started",
            project_id=state["project_id"],
            agent="outline",
            status="running",
        )
    )

    summary = state["idc_output"]["summary"]

    state["outline_output"] = {
        "title": "Generated Outline",
        "sections": [
            "Introduction",
            "Main Development",
            "Conclusion",
        ],
        "source_summary": summary[:200],
        "status": "generated",
    }

    state["events"].append(
        create_event(
            event="outline_completed",
            project_id=state["project_id"],
            agent="outline",
            status="completed",
        )
    )

    return state
