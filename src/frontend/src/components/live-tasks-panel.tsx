'use client';

import { useState } from 'react';

import { fetchLiveTasks } from '@/lib/api';
import type { LiveTaskResponse } from '@/lib/types';

export function LiveTasksPanel() {
  const [data, setData] = useState<LiveTaskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchLiveTasks();
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="rounded-2xl border border-zinc-200 bg-white/70 p-5 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-emerald-600">
            Live LMS Tasks
          </p>
          <h2 className="text-lg font-semibold text-zinc-900">fetched from LearnUs</h2>
        </div>
        <button
          onClick={handleFetch}
          disabled={loading}
          className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
        >
          {loading ? 'Fetching…' : 'Fetch latest'}
        </button>
      </div>
      {error ? (
        <p className="mt-3 text-sm text-rose-600">{error}</p>
      ) : null}
      {data ? (
        <div className="mt-4">
          <p className="text-sm text-zinc-600">
            {data.count} tasks retrieved. Top campuses:
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {data.campus_breakdown.map((entry) => (
              <span
                key={entry.location}
                className="inline-flex items-center gap-2 rounded-full bg-zinc-100 px-3 py-1 text-xs"
              >
                <span className="font-semibold text-zinc-900">{entry.location}</span>
                <span className="text-zinc-500">{entry.count}</span>
              </span>
            ))}
          </div>
          <ul className="mt-4 space-y-2">
            {data.tasks.map((task) => (
              <li key={`${task.task}-${task.course}`} className="rounded-xl border border-zinc-100 bg-zinc-50 px-4 py-3 text-sm">
                <p className="font-semibold text-zinc-900">{task.task}</p>
                <p className="text-zinc-500">{task.location ?? '위치 미정'} · {task.estimated_time}분</p>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
