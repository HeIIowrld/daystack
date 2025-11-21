'use client';

import dynamic from "next/dynamic";

import type { ScheduleItem } from "@/lib/types";

const LeafletMap = dynamic(() => import("./leaflet-map"), {
  ssr: false,
  loading: () => (
    <section className="rounded-2xl border border-dashed border-zinc-200 bg-white/70 p-5 text-zinc-500">
      <p className="text-sm font-medium">Loading map…</p>
      <p className="text-xs">
        This requires a reachable OpenStreetMap tile server; check your network if the map never appears.
      </p>
    </section>
  ),
});

export function MapView({ items }: { items: ScheduleItem[] }) {
  const hasCoords = items.some((item) => item.coordinates);

  if (!hasCoords) {
    return (
      <section className="rounded-2xl border border-zinc-200 bg-white/70 p-5 text-zinc-500">
        <h2 className="text-lg font-semibold text-zinc-900">Route Map</h2>
        <p className="mt-3 text-sm">
          Add locations to your schedule to see them plotted on the map.
        </p>
      </section>
    );
  }

  return (
    <section className="rounded-2xl border border-zinc-200 bg-white/70 p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-emerald-600">Map</p>
          <h2 className="text-lg font-semibold text-zinc-900">Optimized Route</h2>
        </div>
        <span className="text-xs text-zinc-500">
          {items.length} {items.length === 1 ? "stop" : "stops"}
        </span>
      </div>
      <LeafletMap items={items} />
    </section>
  );
}
