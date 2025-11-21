'use client';

import dynamic from "next/dynamic";

import type { ScheduleItem } from "@/lib/types";

const LeafletMap = dynamic(() => import("./leaflet-map"), {
  ssr: false,
  loading: () => (
    <div className="rounded-2xl border border-emerald-100 bg-emerald-50/80 p-5 text-emerald-800">
      <p className="text-sm font-medium">지도를 불러오는 중입니다...</p>
    </div>
  ),
});

export function MapView({ schedule }: { schedule: ScheduleItem[] }) {
  const hasCoordinates = schedule.some((item) => item.coordinates);

  if (!hasCoordinates) {
    return (
      <section className="rounded-2xl border border-dashed border-zinc-200 bg-white/70 p-5 text-zinc-500">
        <h2 className="text-lg font-semibold text-zinc-900">지도를 표시할 수 없습니다</h2>
        <p className="mt-2 text-sm">
          주소를 좌표로 변환할 수 없어 지도를 렌더링하지 못했습니다. NAVER API 키 설정을 확인하세요.
        </p>
      </section>
    );
  }

  return (
    <section className="rounded-2xl border border-emerald-100 bg-white/80 p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-emerald-900">이동 경로</h2>
      <p className="mt-1 text-sm text-emerald-700">일정 순서대로 이동 경로를 확인하세요.</p>
      <LeafletMap schedule={schedule} />
    </section>
  );
}
