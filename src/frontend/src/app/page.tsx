import Image from "next/image";
import Link from "next/link";

import { LiveTasksPanel } from "@/components/live-tasks-panel";
import { MapView } from "@/components/map-view";
import { fetchSampleData } from "@/lib/api";
import {
  OptimizeResponse,
  ScheduleInsights,
  ScheduleItem,
  TodoItem,
} from "@/lib/types";

export const dynamic = "force-dynamic";

function formatTimeRange(item: ScheduleItem) {
  if (item.start_time && item.end_time) {
    return `${item.start_time} - ${item.end_time}`;
  }
  if (item.start_time) {
    return `${item.start_time} -`;
  }
  if (item.end_time) {
    return `- ${item.end_time}`;
  }
  return "Time TBD";
}

function ScheduleSection({
  title,
  items,
}: {
  title: string;
  items: ScheduleItem[];
}) {
  return (
    <section className="rounded-2xl border border-zinc-200 bg-white/70 p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-zinc-900">{title}</h2>
        <span className="text-sm text-zinc-500">{items.length} entries</span>
      </div>
      <div className="mt-4 space-y-3">
        {items.map((item, index) => (
          <div
            key={`${item.name}-${index}`}
            className="rounded-xl border border-zinc-100 bg-zinc-50/60 px-4 py-3"
          >
            <p className="text-sm font-medium text-zinc-500">
              {formatTimeRange(item)}
            </p>
            <p className="text-base font-semibold text-zinc-900">
              {item.name}
            </p>
            {item.location ? (
              <p className="text-sm text-zinc-500">{item.location}</p>
            ) : null}
          </div>
        ))}
      </div>
    </section>
  );
}

function TodoBoard({
  title,
  todos,
}: {
  title: string;
  todos: TodoItem[];
}) {
  return (
    <section className="rounded-2xl border border-zinc-200 bg-white/70 p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-zinc-900">{title}</h2>
        <span className="text-sm text-zinc-500">{todos.length} tasks</span>
      </div>
      <ul className="mt-4 space-y-3">
        {todos.map((todo) => (
          <li
            key={todo.task}
            className="rounded-xl border border-zinc-100 bg-zinc-50/60 px-4 py-3 text-zinc-900"
          >
            <div>
              <p className="font-medium">{todo.task}</p>
              {todo.course_display ? (
                <p className="text-xs text-zinc-500">{todo.course_display}</p>
              ) : null}
              {!todo.course_display && todo.location ? (
                <p className="text-xs text-zinc-500">{todo.location}</p>
              ) : null}
            </div>
            <span className="text-sm font-semibold">
              {todo.estimated_time} min
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}

function RemainingTodoSection({ todos }: { todos: TodoItem[] }) {
  return (
    <section className="rounded-2xl border border-amber-100 bg-amber-50/70 p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-amber-900">
        Remaining Tasks
      </h2>
      {todos.length === 0 ? (
        <p className="mt-4 text-sm text-amber-800">
          Everything is already scheduled. Nicely done!
        </p>
      ) : (
        <ul className="mt-4 space-y-3">
          {todos.map((todo) => (
            <li
              key={todo.task}
              className="rounded-xl border border-amber-100 bg-white/80 px-4 py-3 text-amber-900"
            >
              <span>{todo.task}</span>
              <span className="text-sm font-medium">
                {todo.estimated_time} min
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function InsightsPanel({ insights }: { insights: ScheduleInsights }) {
  return (
    <section className="rounded-2xl border border-zinc-200 bg-white/70 p-5 shadow-sm">
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl bg-zinc-900 px-5 py-4 text-white">
          <p className="text-xs uppercase tracking-[0.3em] text-zinc-400">
            Total Tasks
          </p>
          <p className="mt-2 text-3xl font-semibold">{insights.total_tasks}</p>
        </div>
        <div className="rounded-2xl bg-emerald-50 px-5 py-4 text-emerald-900">
          <p className="text-xs uppercase tracking-[0.3em] text-emerald-700">
            Scheduled
          </p>
          <p className="mt-2 text-3xl font-semibold">
            {insights.scheduled_tasks}
          </p>
        </div>
        <div className="rounded-2xl bg-rose-50 px-5 py-4 text-rose-900">
          <p className="text-xs uppercase tracking-[0.3em] text-rose-700">
            Remaining
          </p>
          <p className="mt-2 text-3xl font-semibold">
            {insights.remaining_tasks}
          </p>
        </div>
      </div>
      <div className="mt-6">
        <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">
          Campus Breakdown
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          {insights.campus_breakdown.map((entry) => (
            <span
              key={entry.location}
              className="inline-flex items-center gap-2 rounded-full border border-zinc-200 px-4 py-1 text-sm"
            >
              <span className="font-semibold text-zinc-900">
                {entry.location}
              </span>
              <span className="text-zinc-500">{entry.count}</span>
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

async function loadSample(): Promise<OptimizeResponse | null> {
  try {
    return await fetchSampleData();
  } catch (error) {
    console.error("Failed to fetch sample data:", error);
    return null;
  }
}

export default async function Home() {
  const data = await loadSample();

  return (
    <div className="min-h-screen bg-zinc-50 py-10 font-sans text-zinc-900">
      <main className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-6">
        <header className="rounded-3xl border border-zinc-200 bg-white px-8 py-10 shadow-md">
          <div className="flex flex-wrap items-center justify-between gap-8">
            <div className="flex flex-wrap items-center gap-8">
              <Image
                src="/daystack-pill.svg"
                alt="DAYSTACK wordmark"
                width={200}
                height={60}
                priority
                unoptimized
              />
              <p className="text-sm font-semibold uppercase tracking-[1.1em] text-emerald-600 whitespace-nowrap">
                Travel-Time Optimizer
              </p>
            </div>
            <Link
              href="/leaderboard"
              className="rounded-full bg-emerald-100 px-6 py-2 text-sm font-semibold text-emerald-800 transition-colors hover:bg-emerald-200"
            >
              View Leaderboard →
            </Link>
          </div>
          <h1 className="mt-4 text-4xl font-semibold text-zinc-900">
            Travel-aware schedule optimizer
          </h1>
          <p className="mt-3 max-w-3xl text-lg text-zinc-600">
            The backend API combines your course schedule, tasks, and travel
            time to build an optimized day plan. Ensure the FastAPI server is
            running locally and map credentials are configured to see live data.
          </p>
          <div className="mt-6 flex flex-wrap gap-4 text-sm text-zinc-500">
            <span className="rounded-full bg-zinc-100 px-4 py-1">
              API base:{" "}
              {process.env.NEXT_PUBLIC_API_BASE_URL ??
                "http://localhost:8000/api"}
            </span>
            {data ? (
              <span className="rounded-full bg-emerald-100 px-4 py-1 text-emerald-800">
                {data.meta.config_ready
                  ? "Naver API credentials detected"
                  : "Using fallback travel-time estimates"}
              </span>
            ) : null}
          </div>
        </header>

        {!data ? (
          <section className="rounded-3xl border border-rose-100 bg-rose-50 px-8 py-10 text-rose-900 shadow-sm">
            <h2 className="text-2xl font-semibold">Backend connection needed</h2>
            <p className="mt-3 text-base">
              Please confirm the FastAPI server is running and reachable.
            </p>
            <pre className="mt-4 rounded-2xl bg-rose-100 px-4 py-3 text-sm font-semibold text-rose-900">
              uvicorn backend.api:app --reload --app-dir src
            </pre>
            <p className="mt-4 text-sm">
              When the server is available, this page will automatically show
              live data including the route map.
            </p>
          </section>
        ) : (
          <>
            <InsightsPanel insights={data.insights} />
            <MapView items={data.optimized_schedule} />
            <LiveTasksPanel />
            <div className="grid gap-6 md:grid-cols-2">
              <ScheduleSection title="Original Schedule" items={data.schedule} />
              <ScheduleSection
                title="Optimized Timeline"
                items={data.optimized_schedule}
              />
              <TodoBoard title="Todo Backlog" todos={data.todos} />
              <RemainingTodoSection todos={data.remaining_todos} />
            </div>
          </>
        )}
      </main>
    </div>
  );
}
