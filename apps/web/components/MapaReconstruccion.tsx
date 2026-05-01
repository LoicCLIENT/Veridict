"use client";

import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

interface MapaReconstruccionProps {
  ubicacion: { lat: number; lon: number };
  trayectorias?: {
    vehiculo: "A" | "B";
    puntos: { lat: number; lon: number; tiempo: number }[];
  }[];
  tiempoActual?: number;
}

export function MapaReconstruccion({
  ubicacion,
  trayectorias = [],
  tiempoActual = 0,
}: MapaReconstruccionProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || "";

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: "mapbox://styles/mapbox/dark-v11",
      center: [ubicacion.lon, ubicacion.lat],
      zoom: 17,
      pitch: 45,
    });

    // Agregar marcador de colision
    new mapboxgl.Marker({ color: "#ef4444" })
      .setLngLat([ubicacion.lon, ubicacion.lat])
      .addTo(map.current);

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, [ubicacion]);

  // Actualizar trayectorias cuando cambia el tiempo
  useEffect(() => {
    if (!map.current || trayectorias.length === 0) return;

    // Aqui se animarian las trayectorias segun tiempoActual
    // Por ahora solo mostramos las lineas completas
  }, [trayectorias, tiempoActual]);

  return (
    <div className="relative w-full h-full min-h-[400px] rounded-lg overflow-hidden">
      <div ref={mapContainer} className="absolute inset-0" />
      {!process.env.NEXT_PUBLIC_MAPBOX_TOKEN && (
        <div className="absolute inset-0 flex items-center justify-center bg-secondary/80">
          <p className="text-muted-foreground">
            Configura NEXT_PUBLIC_MAPBOX_TOKEN para ver el mapa
          </p>
        </div>
      )}
    </div>
  );
}
