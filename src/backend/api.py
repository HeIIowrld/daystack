"""
FastAPI application exposing the YCC scheduler over HTTP.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import uuid

import sys

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import Config
from .geocoding import get_location_coords
from .sample_data import get_sample_schedule, get_sample_todos
from .scheduler import allocate_tasks

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

try:
    from daystack import get_crawler_tasks
except Exception:
    get_crawler_tasks = None


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
    id: Optional[str] = None  # For updates/deletes
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
    course_display: Optional[str] = None
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


class LiveTaskResponse(BaseModel):
    tasks: List[TodoItem]
    count: int
    campus_breakdown: List[CampusBreakdown]


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
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api", tags=["scheduler"])

# In-memory schedule storage (in production, use a database)
_schedule_store: List[dict] = []


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
    sample_schedule = get_sample_schedule()
    # Add IDs to sample schedule items if not present
    schedule = []
    for item in sample_schedule:
        item_dict = dict(item)
        if "id" not in item_dict:
            item_dict["id"] = str(uuid.uuid4())
        schedule.append(ScheduleItem(**item_dict))
    todos = [TodoItem(**item) for item in get_sample_todos()]
    return _run_optimization(schedule, todos)


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize(payload: OptimizeRequest) -> OptimizeResponse:
    """Optimize an arbitrary schedule/task payload."""
    return _run_optimization(payload.schedule, payload.todos)


@router.get("/tasks/live", response_model=LiveTaskResponse)
async def live_tasks() -> LiveTaskResponse:
    """Fetch real LMS assignments using daystack crawler."""
    if not callable(get_crawler_tasks):
        raise HTTPException(
            status_code=503,
            detail="LMS crawler not available on this server.",
        )

    tasks = get_crawler_tasks()
    if not tasks:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch tasks from LMS.",
        )

    campus_counter = defaultdict(int)
    todo_models = []
    for task in tasks:
        todo = TodoItem(**task)
        location = todo.location or "위치 미정"
        campus_counter[location] += 1
        todo_models.append(todo)

    return LiveTaskResponse(
        tasks=todo_models,
        count=len(todo_models),
        campus_breakdown=[
            CampusBreakdown(location=loc, count=count)
            for loc, count in sorted(campus_counter.items())
        ],
    )


# Schedule Management Endpoints
@router.get("/schedule", response_model=List[ScheduleItem])
async def get_schedule() -> List[ScheduleItem]:
    """Get all schedule items."""
    try:
        # If store is empty, return sample schedule with IDs
        if not _schedule_store:
            sample = get_sample_schedule()
            schedule_items = []
            for item in sample:
                item_dict = dict(item)
                # Ensure ID is present
                if "id" not in item_dict:
                    item_dict["id"] = str(uuid.uuid4())
                # Ensure all required fields are present
                if "name" not in item_dict:
                    continue  # Skip invalid items
                try:
                    schedule_items.append(ScheduleItem(**item_dict))
                except Exception as e:
                    print(f"Warning: Skipping invalid schedule item: {e}")
                    continue
            return schedule_items
        return [ScheduleItem(**item) for item in _schedule_store]
    except Exception as e:
        # Log error and return empty list instead of crashing
        print(f"Error in get_schedule: {e}")
        import traceback
        traceback.print_exc()
        return []


@router.post("/schedule", response_model=ScheduleItem)
async def add_schedule_item(item: ScheduleItem) -> ScheduleItem:
    """Add a new schedule item."""
    # Generate ID if not provided
    if not item.id:
        item.id = str(uuid.uuid4())
    
    # Validate time format (only if provided and not empty)
    if item.start_time and item.start_time.strip():
        try:
            # Handle both "HH:MM" and "HH:MM:SS" formats
            time_str = item.start_time.strip()
            if len(time_str) == 5:  # HH:MM
                datetime.strptime(time_str, "%H:%M")
            elif len(time_str) == 8:  # HH:MM:SS
                datetime.strptime(time_str, "%H:%M:%S")
            else:
                raise ValueError("Invalid time format")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_time format. Use HH:MM")
    else:
        item.start_time = None
    
    if item.end_time and item.end_time.strip():
        try:
            # Handle both "HH:MM" and "HH:MM:SS" formats
            time_str = item.end_time.strip()
            if len(time_str) == 5:  # HH:MM
                datetime.strptime(time_str, "%H:%M")
            elif len(time_str) == 8:  # HH:MM:SS
                datetime.strptime(time_str, "%H:%M:%S")
            else:
                raise ValueError("Invalid time format")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_time format. Use HH:MM")
    else:
        item.end_time = None
    
    # Validate time order (only if both are provided)
    if item.start_time and item.end_time:
        # Normalize to HH:MM format for comparison
        start_str = item.start_time[:5] if len(item.start_time) >= 5 else item.start_time
        end_str = item.end_time[:5] if len(item.end_time) >= 5 else item.end_time
        start = datetime.strptime(start_str, "%H:%M")
        end = datetime.strptime(end_str, "%H:%M")
        if end <= start:
            raise HTTPException(status_code=400, detail="end_time must be after start_time")
    
    item_dict = item.model_dump(exclude_none=True)
    _schedule_store.append(item_dict)
    
    # Sort by start_time
    _schedule_store.sort(key=lambda x: x.get("start_time", x.get("end_time", "")))
    
    return ScheduleItem(**item_dict)


@router.put("/schedule/{item_id}", response_model=ScheduleItem)
async def update_schedule_item(item_id: str, item: ScheduleItem) -> ScheduleItem:
    """Update an existing schedule item."""
    # Find item by ID
    index = None
    for i, stored_item in enumerate(_schedule_store):
        if stored_item.get("id") == item_id:
            index = i
            break
    
    if index is None:
        raise HTTPException(status_code=404, detail="Schedule item not found")
    
    # Validate time format (only if provided and not empty)
    if item.start_time and item.start_time.strip():
        try:
            # Handle both "HH:MM" and "HH:MM:SS" formats
            time_str = item.start_time.strip()
            if len(time_str) == 5:  # HH:MM
                datetime.strptime(time_str, "%H:%M")
            elif len(time_str) == 8:  # HH:MM:SS
                datetime.strptime(time_str, "%H:%M:%S")
            else:
                raise ValueError("Invalid time format")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_time format. Use HH:MM")
    else:
        item.start_time = None
    
    if item.end_time and item.end_time.strip():
        try:
            # Handle both "HH:MM" and "HH:MM:SS" formats
            time_str = item.end_time.strip()
            if len(time_str) == 5:  # HH:MM
                datetime.strptime(time_str, "%H:%M")
            elif len(time_str) == 8:  # HH:MM:SS
                datetime.strptime(time_str, "%H:%M:%S")
            else:
                raise ValueError("Invalid time format")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_time format. Use HH:MM")
    else:
        item.end_time = None
    
    # Validate time order (only if both are provided)
    if item.start_time and item.end_time:
        # Normalize to HH:MM format for comparison
        start_str = item.start_time[:5] if len(item.start_time) >= 5 else item.start_time
        end_str = item.end_time[:5] if len(item.end_time) >= 5 else item.end_time
        start = datetime.strptime(start_str, "%H:%M")
        end = datetime.strptime(end_str, "%H:%M")
        if end <= start:
            raise HTTPException(status_code=400, detail="end_time must be after start_time")
    
    # Update item (preserve ID)
    item_dict = item.model_dump(exclude_none=True)
    item_dict["id"] = item_id
    _schedule_store[index] = item_dict
    
    # Sort by start_time
    _schedule_store.sort(key=lambda x: x.get("start_time", x.get("end_time", "")))
    
    return ScheduleItem(**item_dict)


@router.delete("/schedule/{item_id}")
async def delete_schedule_item(item_id: str) -> dict:
    """Delete a schedule item."""
    # Find item by ID
    index = None
    for i, stored_item in enumerate(_schedule_store):
        if stored_item.get("id") == item_id:
            index = i
            break
    
    if index is None:
        raise HTTPException(status_code=404, detail="Schedule item not found")
    
    _schedule_store.pop(index)
    return {"message": "Schedule item deleted", "id": item_id}


@router.post("/schedule/reset")
async def reset_schedule() -> dict:
    """Reset schedule to sample data."""
    global _schedule_store
    sample = get_sample_schedule()
    _schedule_store = []
    for item in sample:
        item_dict = dict(item)
        item_dict["id"] = str(uuid.uuid4())
        _schedule_store.append(item_dict)
    return {"message": "Schedule reset to sample data", "count": len(_schedule_store)}


app.include_router(router)
