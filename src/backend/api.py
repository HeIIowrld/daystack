"""
FastAPI application exposing the YCC scheduler over HTTP.
"""

from __future__ import annotations

from collections import defaultdict
from typing import List, Optional

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import Config
from .geocoding import get_location_coords
from .sample_data import get_sample_schedule, get_sample_todos
from .scheduler import allocate_tasks


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
    location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    type: Optional[str] = None
    coordinates: Optional[Coordinates] = None


class TodoItem(BaseModel):
    task: str
    estimated_time: int = Field(..., gt=0, description="Minutes required")
    location: Optional[str] = None
    deadline: Optional[str] = None
    course: Optional[str] = None
    link: Optional[str] = None
    source: Optional[str] = None


class SchedulerMeta(BaseModel):
    config_ready: bool
    travel_time_buffer: int


class CampusBreakdown(BaseModel):
    location: str
    count: int


class ScheduleInsights(BaseModel):
    total_tasks: int
    scheduled_tasks: int
    remaining_tasks: int
    campus_breakdown: List[CampusBreakdown]


class OptimizeRequest(BaseModel):
    schedule: List[ScheduleItem]
    todos: List[TodoItem]


class OptimizeResponse(BaseModel):
    schedule: List[ScheduleItem]
    todos: List[TodoItem]
    optimized_schedule: List[ScheduleItem]
    remaining_todos: List[TodoItem]
    meta: SchedulerMeta
    insights: ScheduleInsights


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
    return {"status": "ok ok ok"}


@app.get("/health-2", response_model=SchedulerMeta)
async def health():
    """Simple health endpoint for uptime checks."""
    return SchedulerMeta(config_ready=True, travel_time_buffer=1)


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
    def _parse_coordinates(raw: Optional[str]) -> Optional[Coordinates]:
        if not raw:
            return None
        try:
            lng_str, lat_str = raw.split(",", maxsplit=1)
            return Coordinates(lat=float(lat_str), lng=float(lng_str))
        except (ValueError, TypeError):
            return None

    def _attach_coordinates(
        items: List[ScheduleItem],
        cache: dict[str, Coordinates | None],
    ) -> List[ScheduleItem]:
        enhanced: List[ScheduleItem] = []
        for item in items:
            coords = item.coordinates
            if not coords and item.location:
                if item.location not in cache:
                    cache[item.location] = _parse_coordinates(
                        get_location_coords(item.location)
                    )
                coords = cache[item.location]
            enhanced.append(
                item.model_copy(update={"coordinates": coords})
            )
        return enhanced

    coord_cache: dict[str, Coordinates | None] = {}

    schedule_payload = [
        item.model_dump(exclude_none=True, exclude={"coordinates"})
        for item in schedule
    ]
    todo_payload = [item.model_dump(exclude_none=True) for item in todos]

    if not schedule_payload:
        raise HTTPException(status_code=400, detail="Schedule cannot be empty")

    optimized_schedule, remaining = allocate_tasks(
        schedule_payload,
        todo_payload,
        return_summary=True,
    )

    optimized_models = [ScheduleItem(**entry) for entry in optimized_schedule]

    campus_counter = defaultdict(int)
    for todo in todos:
        location = todo.location or "위치 미정"
        campus_counter[location] += 1

    insights = ScheduleInsights(
        total_tasks=len(todos),
        scheduled_tasks=len(todos) - len(remaining),
        remaining_tasks=len(remaining),
        campus_breakdown=[
            CampusBreakdown(location=loc, count=count)
            for loc, count in sorted(campus_counter.items())
        ],
    )

    return OptimizeResponse(
        schedule=_attach_coordinates(schedule, coord_cache),
        todos=todos,
        optimized_schedule=_attach_coordinates(
            optimized_models, coord_cache
        ),
        remaining_todos=[TodoItem(**todo) for todo in remaining],
        meta=SchedulerMeta(
            config_ready=_config_ready(),
            travel_time_buffer=Config.TRAVEL_TIME_BUFFER,
        ),
        insights=insights,
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
