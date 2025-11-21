import Image from "next/image";

import { MapView } from "@/components/map-view";
import { fetchSampleData } from "@/lib/api";
import { OptimizeResponse, ScheduleItem, TodoItem } from "@/lib/types";

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
  return "시간 미정";
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
            className="flex items-center justify-between rounded-xl border border-zinc-100 bg-zinc-50/60 px-4 py-3 text-zinc-900"
          >
            <div>
              <p className="font-medium">{todo.task}</p>
              {todo.course ? (
                <p className="text-xs text-zinc-500">{todo.course}</p>
              ) : null}
            </div>
            <span className="text-sm font-semibold">
              {todo.estimated_time}분
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
        <p className="mt-4 text-sm text-amber-800">모든 작업이 일정에 배치되었습니다.</p>
      ) : (
        <ul className="mt-4 space-y-3">
          {todos.map((todo) => (
            <li
              key={todo.task}
              className="flex items-center justify-between rounded-xl border border-amber-100 bg-white/80 px-4 py-3 text-amber-900"
            >
              <span>{todo.task}</span>
              <span className="text-sm font-medium">{todo.estimated_time}분</span>
            </li>
          ))}
        </ul>
      )}
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
          <div className="flex flex-wrap items-center gap-4">
            <Image
              src="/daystack-logo.svg"
              alt="DAYSTACK logo"
              width={160}
              height={40}
              priority
              unoptimized
            />
            <p className="text-sm uppercase tracking-[0.3em] text-emerald-600">
              Travel-Time Optimizer
            </p>
          </div>
          <h1 className="mt-4 text-4xl font-semibold text-zinc-900">
            이동 시간을 고려한 일정 최적화
          </h1>
          <p className="mt-3 max-w-3xl text-lg text-zinc-600">
            DAYSTACK 메인 컨트롤러의 스케줄/과제 데이터를 FastAPI 백엔드에서
            가져와 시각화합니다. 백엔드가 Coursemos 크롤러를 통해 과제를 모으고
            스케줄러에 전달하면, 이 페이지는 결과를 즉시 보여줍니다.
          </p>
          <div className="mt-6 flex flex-wrap gap-4 text-sm text-zinc-500">
            <span className="rounded-full bg-zinc-100 px-4 py-1">
              API base: {process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api"}
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
            <h2 className="text-2xl font-semibold">백엔드 연결 필요</h2>
            <p className="mt-3 text-base">
              FastAPI 서버가 실행 중인지 확인하세요:
            </p>
            <pre className="mt-4 rounded-2xl bg-rose-100 px-4 py-3 text-sm font-semibold text-rose-900">
              uvicorn backend.api:app --reload --app-dir src
            </pre>
            <p className="mt-4 text-sm">
              서버가 준비되면 이 페이지가 자동으로 샘플 결과를 표시합니다.
            </p>
          </section>
        ) : (
          <>
            <MapView schedule={data.optimized_schedule} />
            <div className="grid gap-6 md:grid-cols-2">
              <ScheduleSection title="Original Schedule" items={data.schedule} />
              <ScheduleSection title="Optimized Timeline" items={data.optimized_schedule} />
              <TodoBoard title="Todo Backlog" todos={data.todos} />
              <RemainingTodoSection todos={data.remaining_todos} />
            </div>
          </>
        )}
      </main>
    </div>
  );
}
