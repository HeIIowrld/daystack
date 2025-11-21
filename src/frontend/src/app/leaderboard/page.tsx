type LeaderboardEntry = {
  name: string;
  role: string;
  tasksCompleted: number;
  focusedMinutes: number;
  streakDays: number;
};

const leaderboardData: LeaderboardEntry[] = [
  {
    name: "Alex Rivera",
    role: "Product Design",
    tasksCompleted: 18,
    focusedMinutes: 1260,
    streakDays: 9,
  },
  {
    name: "Mina Cho",
    role: "Data Science",
    tasksCompleted: 15,
    focusedMinutes: 1185,
    streakDays: 7,
  },
  {
    name: "Jules Hart",
    role: "Backend",
    tasksCompleted: 13,
    focusedMinutes: 990,
    streakDays: 6,
  },
  {
    name: "Priya Desai",
    role: "Mobile",
    tasksCompleted: 11,
    focusedMinutes: 845,
    streakDays: 5,
  },
  {
    name: "Noor Amini",
    role: "Research",
    tasksCompleted: 10,
    focusedMinutes: 770,
    streakDays: 4,
  },
  {
    name: "Jonas Kim",
    role: "Front-end",
    tasksCompleted: 9,
    focusedMinutes: 705,
    streakDays: 3,
  },
];

function formatHours(minutes: number) {
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes.toString().padStart(2, "0")}m`;
}

function Medal({ rank }: { rank: number }) {
  const palette: Record<number, string> = {
    1: "from-amber-200 to-amber-400 text-amber-900 border-amber-200",
    2: "from-zinc-100 to-zinc-300 text-zinc-900 border-zinc-200",
    3: "from-orange-100 to-orange-300 text-orange-900 border-orange-200",
  };
  const colors =
    palette[rank] ?? "from-zinc-100 to-zinc-200 text-zinc-900 border-zinc-200";

  return (
    <span
      className={`inline-flex items-center justify-center rounded-full border px-3 py-1 text-sm font-semibold shadow-sm bg-gradient-to-br ${
        colors
      }`}
    >
      #{rank}
    </span>
  );
}

export default function LeaderboardPage() {
  const sorted = [...leaderboardData].sort(
    (a, b) => b.focusedMinutes - a.focusedMinutes,
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-50 via-white to-emerald-50 px-6 py-12 text-zinc-900">
      <main className="mx-auto flex w-full max-w-5xl flex-col gap-8">
        <header className="rounded-3xl border border-emerald-100 bg-white/90 px-8 py-10 shadow-lg shadow-emerald-100/70">
          <div className="flex flex-wrap items-center gap-3">
            <span className="rounded-full bg-emerald-100 px-4 py-1 text-sm font-semibold text-emerald-800">
              Team leaderboard
            </span>
            <p className="text-sm uppercase tracking-[0.25em] text-emerald-700">
              Time used on meaningful tasks
            </p>
          </div>
          <h1 className="mt-4 text-4xl font-semibold">Focus time champions</h1>
          <p className="mt-3 max-w-2xl text-base text-zinc-600">
            Ranking is based on total focused minutes logged on scheduled
            tasks. Keep your streak alive to climb the board and unlock team
            shoutouts.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          {sorted.slice(0, 3).map((entry, index) => (
            <div
              key={entry.name}
              className="flex flex-col rounded-2xl border border-zinc-200 bg-white/90 px-6 py-5 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-full bg-emerald-100 text-lg font-semibold text-emerald-800">
                    {entry.name.slice(0, 1)}
                  </div>
                  <div>
                    <p className="text-base font-semibold text-zinc-900">
                      {entry.name}
                    </p>
                    <p className="text-sm text-zinc-500">{entry.role}</p>
                  </div>
                </div>
                <Medal rank={index + 1} />
              </div>
              <div className="mt-4 flex items-center justify-between text-sm text-zinc-600">
                <span className="font-semibold text-zinc-900">
                  {formatHours(entry.focusedMinutes)}
                </span>
                <span>{entry.tasksCompleted} tasks shipped</span>
                <span className="rounded-full bg-emerald-50 px-3 py-1 text-emerald-700">
                  {entry.streakDays}-day streak
                </span>
              </div>
            </div>
          ))}
        </section>

        <section className="rounded-3xl border border-zinc-200 bg-white/95 p-8 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-semibold text-zinc-900">
                Full leaderboard
              </h2>
              <p className="text-sm text-zinc-500">
                Sorted by total focused time on tasks.
              </p>
            </div>
            <span className="rounded-full bg-emerald-100 px-4 py-1 text-sm font-semibold text-emerald-800">
              {sorted.reduce((total, item) => total + item.focusedMinutes, 0)}{" "}
              min logged this week
            </span>
          </div>

          <div className="mt-6 overflow-hidden rounded-2xl border border-zinc-100">
            <table className="min-w-full divide-y divide-zinc-100 text-sm">
              <thead className="bg-zinc-50 text-left text-xs font-semibold uppercase tracking-wide text-zinc-500">
                <tr>
                  <th className="px-4 py-3">Rank</th>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Focused time</th>
                  <th className="px-4 py-3">Tasks</th>
                  <th className="px-4 py-3">Streak</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 bg-white">
                {sorted.map((entry, index) => (
                  <tr key={entry.name} className="hover:bg-emerald-50/40">
                    <td className="px-4 py-3 font-semibold text-zinc-500">
                      #{index + 1}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-zinc-100 text-sm font-semibold text-zinc-700">
                          {entry.name.slice(0, 1)}
                        </div>
                        <div>
                          <p className="font-semibold text-zinc-900">
                            {entry.name}
                          </p>
                          <p className="text-xs text-zinc-500">{entry.role}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 font-semibold text-emerald-800">
                      {formatHours(entry.focusedMinutes)}
                    </td>
                    <td className="px-4 py-3 text-zinc-600">
                      {entry.tasksCompleted} tasks
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-zinc-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                        {entry.streakDays} days
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}
