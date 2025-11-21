'use client';

import { useEffect, useMemo } from "react";
import { MapContainer, Marker, Polyline, TileLayer, Tooltip } from "react-leaflet";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import type { ScheduleItem } from "@/lib/types";

export default function LeafletMap({ schedule }: { schedule: ScheduleItem[] }) {
  useEffect(() => {
    async function setupIcons() {
      const L = await import("leaflet");
      const DefaultIcon = L.icon({
        iconRetinaUrl: markerIcon2x.src,
        iconUrl: markerIcon.src,
        shadowUrl: markerShadow.src,
        iconSize: [25, 41],
        iconAnchor: [12, 41],
      });
      L.Marker.prototype.options.icon = DefaultIcon;
    }

    setupIcons();
  }, []);

  const points = useMemo(
    () =>
      schedule
        .filter((item) => item.coordinates)
        .map((item, index) => ({
          id: `${item.name}-${index}`,
          title: item.name,
          position: [item.coordinates!.lat, item.coordinates!.lng] as [number, number],
        })),
    [schedule],
  );

  if (points.length === 0) {
    return null;
  }

  const center = points[0].position;
  const pathPositions = points.map((point) => point.position);

  return (
    <div className="mt-4 overflow-hidden rounded-2xl">
      <MapContainer
        center={center}
        zoom={12}
        scrollWheelZoom={false}
        style={{ width: "100%", height: "360px" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Polyline positions={pathPositions} pathOptions={{ color: "#10b981", weight: 4 }} />
        {points.map((point, index) => (
          <Marker position={point.position} key={point.id}>
            <Tooltip>{`${index + 1}. ${point.title}`}</Tooltip>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
