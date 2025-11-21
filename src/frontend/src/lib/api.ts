import { OptimizeResponse, ScheduleItem, TodoItem } from "@/lib/types";

const DEFAULT_API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

async function request<T>(
  path: string,
  init?: RequestInit,
  options?: { revalidate?: number | false },
): Promise<T> {
  const url = `${DEFAULT_API_BASE_URL}${path}`;
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
