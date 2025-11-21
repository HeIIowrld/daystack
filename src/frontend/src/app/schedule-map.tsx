"use client";

import Image from "next/image";
import { useMemo } from "react";

import type { ScheduleItem } from "@/lib/types";

type Marker = {
  label: string;
  time?: string;
  lat: number;
  lng: number;
};

function estimateZoom(spread: number): number {
  if (spread < 0.01) return 15;
  if (spread < 0.05) return 14;
  if (spread < 0.1) return 13;
  if (spread < 0.25) return 12;
  if (spread < 0.5) return 11;
  if (spread < 1) return 10;
  return 9;
}

function buildStaticMapUrl(markers: Marker[]): string | null {
  if (markers.length === 0) {
    return null;
  }

  const lats = markers.map((m) => m.lat);
  const lngs = markers.map((m) => m.lng);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLng = Math.min(...lngs);
  const maxLng = Math.max(...lngs);

  const centerLat = (minLat + maxLat) / 2;
  const centerLng = (minLng + maxLng) / 2;
  const spread = Math.max(maxLat - minLat, maxLng - minLng);
  const zoom = markers.length === 1 ? 15 : estimateZoom(spread);

  const markerParam = markers
    .map((m) => `${m.lat},${m.lng},lightblue1`)
    .join("|");

  const params = new URLSearchParams({
    center: `${centerLat},${centerLng}`,
    zoom: zoom.toString(),
    size: "900x360",
    markers: markerParam,
  });

  return `https://staticmap.openstreetmap.de/staticmap.php?${params.toString()}`;
}

export function ScheduleMap({ items }: { items: ScheduleItem[] }) {
  const markers = useMemo<Marker[]>(() => {
    return items
      .filter((item) => item.coordinates)
      .map((item) => ({
        label: item.name,
        time:
          item.start_time && item.end_time
            ? `${item.start_time} - ${item.end_time}`
            : item.start_time ?? item.end_time,
        lat: item.coordinates!.lat,
        lng: item.coordinates!.lng,
      }));
  }, [items]);

  const mapUrl = useMemo(() => buildStaticMapUrl(markers), [markers]);

  if (!mapUrl) {
    return (
      <section className="rounded-2xl border border-zinc-200 bg-white/70 p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-zinc-900">Route Map</h2>
        <p className="mt-3 text-sm text-zinc-600">
          No coordinates returned yet. Add locations to your schedule to see
          them plotted on the map.
        </p>
      </section>
    );
  }

  return (
    <section className="rounded-2xl border border-zinc-200 bg-white/70 p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-emerald-600">
            Map
          </p>
          <h2 className="text-lg font-semibold text-zinc-900">
            Optimized Route
          </h2>
        </div>
        <span className="text-xs text-zinc-500">
          {markers.length} {markers.length === 1 ? "stop" : "stops"}
        </span>
      </div>

      <div className="mt-4 overflow-hidden rounded-xl border border-zinc-100 bg-zinc-50">
        <div className="relative h-[360px] w-full">
          <Image
            src={mapUrl}
            alt="Map preview of the optimized schedule"
            fill
            sizes="(max-width: 768px) 100vw, 100vw"
            className="object-cover"
            unoptimized
            priority
          />
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2 text-xs text-zinc-600">
        {markers.map((marker, idx) => (
          <span
            key={`${marker.label}-${idx}`}
            className="inline-flex items-center gap-2 rounded-full bg-zinc-100 px-3 py-1"
          >
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-600 text-[11px] font-semibold text-white">
              {idx + 1}
            </span>
            <span className="font-medium text-zinc-800">{marker.label}</span>
            {marker.time ? (
              <span className="text-zinc-500">({marker.time})</span>
            ) : null}
          </span>
        ))}
      </div>
    </section>
  );
}
