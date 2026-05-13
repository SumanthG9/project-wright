import asyncio
import json

from backend.agents.graph import graph


async def main():
    initial_state = {
        "project_id": 3,
        "current_draft_id": 1,
        "extracted_text": "Hello Project Wright",
        "active_agent": "",
        "pipeline_status": "running",
        "retry_count": 0,
        "events": [],
    }

    print("Running graph...\n")

    result = await graph.ainvoke(initial_state)

    print("Graph completed:\n")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
