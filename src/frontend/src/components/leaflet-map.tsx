'use client';

import { MapContainer, Marker, Polyline, TileLayer, Tooltip } from "react-leaflet";
import L from "leaflet";
import { useMemo } from "react";

import type { ScheduleItem } from "@/lib/types";

export default function LeafletMap({ items }: { items: ScheduleItem[] }) {
  const points = useMemo(
    () =>
      items
        .filter((item) => item.coordinates)
        .map((item, index) => ({
          id: `${item.name}-${index}`,
          label: item.name,
          time:
            item.start_time && item.end_time
              ? `${item.start_time} - ${item.end_time}`
              : item.start_time ?? item.end_time,
          lat: item.coordinates!.lat,
          lng: item.coordinates!.lng,
        })),
    [items],
  );

  if (points.length === 0) {
    return null;
  }

  const center = points[0];
  const icon = L.divIcon({
    className: "",
    html: `<div style="
        width: 18px;
        height: 18px;
        border-radius: 9999px;
        background: #10b981;
        border: 3px solid #ffffff;
        box-shadow: 0 6px 12px rgba(16, 24, 40, 0.35);
      "></div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });

  const path = points.map((p) => [p.lat, p.lng]) as L.LatLngExpression[];

  return (
    <div className="mt-4 overflow-hidden rounded-xl border border-zinc-100 bg-zinc-50">
      <MapContainer
        center={[center.lat, center.lng]}
        zoom={13}
        scrollWheelZoom={false}
        style={{ width: "100%", height: "360px" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        />
        <Polyline positions={path} pathOptions={{ color: "#10b981", weight: 4 }} />
        {points.map((point, index) => (
          <Marker position={[point.lat, point.lng]} key={point.id} icon={icon}>
            <Tooltip>{`${index + 1}. ${point.label}`}</Tooltip>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
