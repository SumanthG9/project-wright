from fastapi import APIRouter, HTTPException

from backend.pipeline.schemas import (
    ApprovalRequest,
    PipelineEventsResponse,
    PipelineHistoryResponse,
    PipelineStartRequest,
    PipelineStatusResponse,
)
from backend.pipeline.service import (
    approve_pipeline,
    get_pipeline_events,
    get_pipeline_history,
    get_pipeline_status,
    reject_pipeline,
    resume_pipeline,
    start_pipeline,
)

router = APIRouter(tags=["Pipeline"])


@router.post("/start")
async def start_pipeline_route(
    payload: PipelineStartRequest,
):
    workflow_id, state = await start_pipeline(
        project_id=payload.project_id,
        draft_id=payload.draft_id,
    )

    return {
        "workflow_id": workflow_id,
        "status": state["pipeline_status"],
    }


@router.post("/{workflow_id}/approve")
async def approve_pipeline_route(
    workflow_id: str,
    payload: ApprovalRequest,
):
    try:
        state = await approve_pipeline(workflow_id)

        return {
            "workflow_id": workflow_id,
            "status": state["pipeline_status"],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.post("/{workflow_id}/reject")
async def reject_pipeline_route(
    workflow_id: str,
    payload: ApprovalRequest,
):
    try:
        state = await reject_pipeline(workflow_id)

        return {
            "workflow_id": workflow_id,
            "status": state["pipeline_status"],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.post("/{workflow_id}/resume")
async def resume_pipeline_route(
    workflow_id: str,
):
    try:
        state = await resume_pipeline(workflow_id)

        return {
            "workflow_id": workflow_id,
            "status": state["pipeline_status"],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get(
    "/{workflow_id}/status",
    response_model=PipelineStatusResponse,
)
async def get_pipeline_status_route(
    workflow_id: str,
):
    try:
        state = get_pipeline_status(workflow_id)

        return PipelineStatusResponse(
            workflow_id=workflow_id,
            project_id=state["project_id"],
            status=state["pipeline_status"],
            active_agent=state["active_agent"],
            paused=state["paused"],
            waiting_for_input=state["waiting_for_input"],
            approval_status=state["approval_status"],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get(
    "/{workflow_id}/history",
    response_model=PipelineHistoryResponse,
)
async def get_pipeline_history_route(
    workflow_id: str,
):
    try:
        state = get_pipeline_history(workflow_id)

        return PipelineHistoryResponse(
            workflow_id=workflow_id,
            project_id=state["project_id"],
            status=state["pipeline_status"],
            active_agent=state["active_agent"],
            paused=state["paused"],
            waiting_for_input=state["waiting_for_input"],
            approval_status=state["approval_status"],
            retry_count=state["retry_count"],
            event_count=len(state["events"]),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get(
    "/{workflow_id}/events",
    response_model=PipelineEventsResponse,
)
async def get_pipeline_events_route(
    workflow_id: str,
):
    try:
        events = get_pipeline_events(workflow_id)

        return PipelineEventsResponse(
            workflow_id=workflow_id,
            events=events,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
