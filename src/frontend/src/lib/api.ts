import {
  LiveTaskResponse,
  OptimizeResponse,
  ScheduleItem,
  TodoItem,
} from "@/lib/types";

const DEFAULT_API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

async function request<T>(
  path: string,
  init?: RequestInit,
  options?: { revalidate?: number | false },
): Promise<T> {
  const url = `${DEFAULT_API_BASE_URL}${path}`;
  
  try {
    const response = await fetch(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      cache: options?.revalidate === false ? "no-store" : undefined,
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(`API request failed (${response.status}): ${detail}`);
    }

    return await response.json();
  } catch (error: any) {
    // Handle network errors
    if (error.name === "TypeError" && error.message.includes("fetch")) {
      throw new Error(
        `Network error: Cannot connect to API at ${url}. ` +
        `Please ensure the FastAPI server is running at ${DEFAULT_API_BASE_URL.replace("/api", "")}`
      );
    }
    throw error;
  }
}

export async function fetchSampleData(): Promise<OptimizeResponse> {
  return request<OptimizeResponse>("/sample", undefined, { revalidate: false });
}

export async function optimizeSchedule(payload: {
  schedule: ScheduleItem[];
  todos: TodoItem[];
}): Promise<OptimizeResponse> {
  return request<OptimizeResponse>(
    "/optimize",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    { revalidate: false },
  );
}

export async function fetchLiveTasks(): Promise<LiveTaskResponse> {
  return request<LiveTaskResponse>('/tasks/live', undefined, { revalidate: false });
}

// Schedule Management Functions
export async function fetchSchedule(): Promise<ScheduleItem[]> {
  return request<ScheduleItem[]>('/schedule', undefined, { revalidate: false });
}

export async function addScheduleItem(item: ScheduleItem): Promise<ScheduleItem> {
  return request<ScheduleItem>(
    '/schedule',
    {
      method: 'POST',
      body: JSON.stringify(item),
    },
    { revalidate: false },
  );
}

export async function updateScheduleItem(
  itemId: string,
  item: ScheduleItem,
): Promise<ScheduleItem> {
  return request<ScheduleItem>(
    `/schedule/${itemId}`,
    {
      method: 'PUT',
      body: JSON.stringify(item),
    },
    { revalidate: false },
  );
}

export async function deleteScheduleItem(itemId: string): Promise<{ message: string; id: string }> {
  return request<{ message: string; id: string }>(
    `/schedule/${itemId}`,
    {
      method: 'DELETE',
    },
    { revalidate: false },
  );
}

export async function resetSchedule(): Promise<{ message: string; count: number }> {
  return request<{ message: string; count: number }>(
    '/schedule/reset',
    {
      method: 'POST',
    },
    { revalidate: false },
  );
}