"""
FastAPI application exposing the YCC scheduler over HTTP.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.config import Config
from backend.location_utils import ensure_coordinates
from backend.sample_data import get_sample_schedule, get_sample_todos
from backend.scheduler import allocate_tasks


def _config_ready() -> bool:
    """Return True if the required Naver credentials are configured."""
    try:
        Config.validate()
        return True
    except ValueError:
        return False


class Coordinates(BaseModel):
    lat: float
    lng: float


class ScheduleItem(BaseModel):
    name: str
    location: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    type: str | None = None
    coordinates: Coordinates | None = None


class TodoItem(BaseModel):
    task: str
    estimated_time: int = Field(..., gt=0, description="Minutes required")
    deadline: str | None = None
    course: str | None = None


class SchedulerMeta(BaseModel):
    config_ready: bool
    travel_time_buffer: int


class OptimizeRequest(BaseModel):
    schedule: List[ScheduleItem]
    todos: List[TodoItem]


class OptimizeResponse(BaseModel):
    schedule: List[ScheduleItem]
    todos: List[TodoItem]
    optimized_schedule: List[ScheduleItem]
    remaining_todos: List[TodoItem]
    meta: SchedulerMeta


app = FastAPI(
    title="YCC Scheduler API",
    version="0.1.0",
    description="HTTP interface for schedule optimization and Coursemos data.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api", tags=["scheduler"])


@app.get("/health")
async def health():
    """Simple health endpoint for uptime checks."""
    return {"status": "ok"}


@router.get("/status", response_model=SchedulerMeta)
async def status() -> SchedulerMeta:
    """Report configuration readiness and other metadata."""
    return SchedulerMeta(
        config_ready=_config_ready(),
        travel_time_buffer=Config.TRAVEL_TIME_BUFFER,
    )


def _run_optimization(
    schedule: List[ScheduleItem],
    todos: List[TodoItem],
) -> OptimizeResponse:
    schedule_payload = [
        item.model_dump(exclude_none=True) for item in schedule
    ]
    todo_payload = [item.model_dump(exclude_none=True) for item in todos]

    if not schedule_payload:
        raise HTTPException(status_code=400, detail="Schedule cannot be empty")

    optimized_schedule, remaining = allocate_tasks(
        schedule_payload,
        todo_payload,
        return_summary=True,
    )

    schedule_with_coords = ensure_coordinates(schedule_payload)
    optimized_with_coords = ensure_coordinates(optimized_schedule)

    optimized_models = [
        ScheduleItem(**entry) for entry in optimized_with_coords
    ]

    return OptimizeResponse(
        schedule=[ScheduleItem(**entry) for entry in schedule_with_coords],
        todos=todos,
        optimized_schedule=optimized_models,
        remaining_todos=[TodoItem(**todo) for todo in remaining],
        meta=SchedulerMeta(
            config_ready=_config_ready(),
            travel_time_buffer=Config.TRAVEL_TIME_BUFFER,
        ),
    )


@router.get("/sample", response_model=OptimizeResponse)
async def sample_data() -> OptimizeResponse:
    """Return sample schedule, tasks, and the optimized output."""
    schedule = [ScheduleItem(**item) for item in get_sample_schedule()]
    todos = [TodoItem(**item) for item in get_sample_todos()]
    return _run_optimization(schedule, todos)


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize(payload: OptimizeRequest) -> OptimizeResponse:
    """Optimize an arbitrary schedule/task payload."""
    return _run_optimization(payload.schedule, payload.todos)


app.include_router(router)
