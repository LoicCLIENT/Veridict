"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { MapPin } from "lucide-react";
import type { EscenaSimulacionData } from "@veridict/types";
import { AccidentScene2D, AccidentSceneData, EscenaSimulacionView } from "./reconstruction";
import {
  VisualizationControls,
  VisualizationSettings,
  defaultVisualizationSettings,
} from "./reconstruction/VisualizationControls";

interface MapaReconstruccionProps {
  ubicacion: { lat: number; lon: number };
  /** Reconstrucción dinámica producida por el SimulationAgent (LLM). Si llega,
   * tiene prioridad sobre `sceneData`. */
  escenaSimulacion?: EscenaSimulacionData | null;
  /** Compatibilidad: AccidentSceneData (mocks legacy con A/B). */
  sceneData?: AccidentSceneData;
  trayectorias?: {
    vehiculo: "A" | "B";
    puntos: { lat: number; lon: number; tiempo: number }[];
  }[];
  tiempoActual?: number;
  onTimeChange?: (time: number) => void;
  compact?: boolean;
  /** Acción que dispara el SimulationAgent (LLM) en el backend. Cuando se
   * proporciona, el placeholder vacío muestra un botón directo. */
  onGenerarSimulacion?: () => void;
  generandoSimulacion?: boolean;
}

export function MapaReconstruccion({
  ubicacion,
  escenaSimulacion,
  sceneData,
  trayectorias = [],
  tiempoActual = 0,
  onTimeChange,
  compact = false,
  onGenerarSimulacion,
  generandoSimulacion = false,
}: MapaReconstruccionProps) {
  const hasDynamicScene = !!(escenaSimulacion && Array.isArray(escenaSimulacion.actores) && escenaSimulacion.actores.length > 0);
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<any>(null);
  const [mapboxLoaded, setMapboxLoaded] = useState(false);
  const [hasToken, setHasToken] = useState(false);
  const [viewMode, setViewMode] = useState<"reconstruction" | "satellite">("reconstruction");
  const [currentTime, setCurrentTime] = useState(tiempoActual);
  const [isPlaying, setIsPlaying] = useState(false);
  const [settings, setSettings] = useState<VisualizationSettings>(defaultVisualizationSettings);
  const [centerTarget, setCenterTarget] = useState<"A" | "B" | "impact" | "overview" | null>(null);

  // Playback interval ref
  const playbackRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
    setHasToken(!!token && token.length > 0);

    if (!token || !mapContainer.current || map.current) return;

    import("mapbox-gl").then((mapboxgl) => {
      mapboxgl.default.accessToken = token;

      map.current = new mapboxgl.default.Map({
        container: mapContainer.current!,
        style: "mapbox://styles/mapbox/dark-v11",
        center: [ubicacion.lon, ubicacion.lat],
        zoom: 17,
        pitch: 45,
      });

      new mapboxgl.default.Marker({ color: "#ef4444" })
        .setLngLat([ubicacion.lon, ubicacion.lat])
        .addTo(map.current);

      setMapboxLoaded(true);
    }).catch(console.error);

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, [ubicacion]);

  // Auto-play with speed control
  useEffect(() => {
    if (isPlaying) {
      const intervalMs = 50 / settings.playbackSpeed;
      playbackRef.current = setInterval(() => {
        setCurrentTime((prev) => {
          const next = prev + 1;
          if (next >= 100) {
            if (settings.loop) {
              return 0;
            }
            setIsPlaying(false);
            return 100;
          }
          return next;
        });
      }, intervalMs);
    }
    return () => {
      if (playbackRef.current) clearInterval(playbackRef.current);
    };
  }, [isPlaying, settings.playbackSpeed, settings.loop]);

  // Sync with external time
  useEffect(() => {
    setCurrentTime(tiempoActual);
  }, [tiempoActual]);

  // Notify time changes
  useEffect(() => {
    onTimeChange?.(currentTime);
  }, [currentTime, onTimeChange]);

  const handlePlayPause = useCallback(() => {
    if (currentTime >= 100) {
      setCurrentTime(0);
    }
    setIsPlaying(!isPlaying);
  }, [isPlaying, currentTime]);

  const handleTimeChange = useCallback((time: number) => {
    setCurrentTime(time);
    setIsPlaying(false);
  }, []);

  const handleReset = useCallback(() => {
    setCurrentTime(0);
    setIsPlaying(false);
  }, []);

  const handleCenterOn = useCallback((target: "A" | "B" | "impact" | "overview") => {
    setCenterTarget(target);
    // Reset after a short delay to allow re-centering
    setTimeout(() => setCenterTarget(null), 100);
  }, []);

  // Compact mode (for embeds)
  if (compact) {
    return (
      <div className="relative w-full h-72 rounded-lg overflow-hidden">
        {hasDynamicScene ? (
          <EscenaSimulacionView
            data={escenaSimulacion!}
            currentTime={currentTime}
            showMeasurements={settings.showMeasurements}
            showTrajectories={settings.showTrajectories}
            showGrid={settings.showGrid}
            compact={true}
          />
        ) : sceneData ? (
          <AccidentScene2D
            data={sceneData}
            currentTime={currentTime}
            showMeasurements={settings.showMeasurements}
            showTrajectories={settings.showTrajectories}
            showGrid={settings.showGrid}
            compact={true}
          />
        ) : (
          <EmptyScenePlaceholder />
        )}{/* keep playback bar */}
        {/* Simple playback bar */}
        <div className="absolute bottom-3 left-3 right-3 z-20">
          <div className="bg-[#0a0a0a]/90 backdrop-blur-sm rounded-lg p-2 border border-white/[0.06]">
            <div className="flex items-center gap-2">
              <button
                onClick={handlePlayPause}
                className={`p-1.5 rounded transition-colors ${
                  isPlaying ? "bg-red-500/20 text-red-400" : "bg-[#C2E94B]/20 text-[#C2E94B]"
                }`}
              >
                {isPlaying ? (
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                    <rect x="6" y="4" width="4" height="16" />
                    <rect x="14" y="4" width="4" height="16" />
                  </svg>
                ) : (
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                )}
              </button>
              <input
                type="range"
                min="0"
                max="100"
                value={currentTime}
                onChange={(e) => handleTimeChange(Number(e.target.value))}
                className="flex-1 h-1 bg-zinc-800 rounded-full appearance-none cursor-pointer
                  [&::-webkit-slider-thumb]:appearance-none
                  [&::-webkit-slider-thumb]:w-2
                  [&::-webkit-slider-thumb]:h-2
                  [&::-webkit-slider-thumb]:rounded-full
                  [&::-webkit-slider-thumb]:bg-[#C2E94B]"
              />
              <span className="text-[10px] font-mono text-zinc-500">{currentTime}%</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Full mode with controls
  const renderReconstructionView = () => (
    <div className="relative w-full h-full min-h-[500px]">
      {hasDynamicScene ? (
        <EscenaSimulacionView
          data={escenaSimulacion!}
          currentTime={currentTime}
          showMeasurements={settings.showMeasurements}
          showTrajectories={settings.showTrajectories}
          showGrid={settings.showGrid}
          showImpactZone={settings.showImpactZone}
        />
      ) : sceneData ? (
        <AccidentScene2D
          data={{
            ...sceneData,
            // Apply vehicle colors from settings
          }}
          currentTime={currentTime}
          showMeasurements={settings.showMeasurements}
          showTrajectories={settings.showTrajectories}
          showGrid={settings.showGrid}
          vehicleAColor={settings.vehicleA.color}
          vehicleBColor={settings.vehicleB.color}
          centerTarget={centerTarget}
          showSpeedLabels={settings.showSpeedLabels}
          showImpactZone={settings.showImpactZone}
          viewMode={settings.viewMode}
        />
      ) : (
        <EmptyScenePlaceholder
          onGenerar={onGenerarSimulacion}
          generando={generandoSimulacion}
        />
      )}

      {/* Coordinates badge */}
      <div className="absolute bottom-3 left-3 bg-[#0a0a0a]/80 px-3 py-2 rounded-lg backdrop-blur-sm z-20 border border-white/[0.04]">
        <div className="flex items-center gap-2 text-xs text-zinc-500">
          <MapPin className="w-3 h-3 text-[#C2E94B]" />
          <span className="font-mono">
            {ubicacion.lat.toFixed(4)}, {ubicacion.lon.toFixed(4)}
          </span>
        </div>
      </div>
    </div>
  );

  if (hasToken && viewMode === "satellite") {
    return (
      <div className="space-y-3">
        <div className="relative w-full h-[500px] rounded-lg overflow-hidden">
          <div ref={mapContainer} className="absolute inset-0" />
          {!mapboxLoaded && (
            <div className="absolute inset-0 flex items-center justify-center bg-[#0d110d]">
              <div className="flex flex-col items-center gap-3">
                <div className="w-8 h-8 border-2 border-[#C2E94B] border-t-transparent rounded-full animate-spin" />
                <span className="text-sm text-zinc-500">Cargando mapa...</span>
              </div>
            </div>
          )}
          <div className="absolute top-4 right-4 z-10">
            <button
              onClick={() => setViewMode("reconstruction")}
              className="px-3 py-1.5 rounded text-xs font-medium bg-[#0a0a0a]/80 text-zinc-400 hover:text-white border border-white/[0.06] transition-colors"
            >
              Vista Técnica
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Descripción del SimulationAgent ahora vive dentro de la escena (chip
          colapsable). Eliminamos la duplicación externa que tapaba la curva. */}
      {/* Visualization controls */}
      <VisualizationControls
        settings={settings}
        onSettingsChange={setSettings}
        currentTime={currentTime}
        isPlaying={isPlaying}
        onPlayPause={handlePlayPause}
        onTimeChange={handleTimeChange}
        onReset={handleReset}
        onCenterOn={handleCenterOn}
      />

      {/* Scene */}
      <div className="relative w-full rounded-lg overflow-hidden border border-white/[0.06]">
        {renderReconstructionView()}

        {/* View mode toggle (only show if Mapbox available) */}
        {hasToken && (
          <div className="absolute top-4 right-4 z-20">
            <button
              onClick={() => setViewMode("satellite")}
              className="px-3 py-1.5 rounded text-xs font-medium bg-[#0a0a0a]/80 text-zinc-400 hover:text-white border border-white/[0.06] transition-colors"
            >
              Vista Satélite
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function EmptyScenePlaceholder({
  onGenerar,
  generando = false,
}: { onGenerar?: () => void; generando?: boolean } = {}) {
  return (
    <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#0d110d] text-zinc-500 text-sm font-mono p-6 text-center gap-3">
      <span className="text-3xl">🛣️</span>
      <span>Reconstrucción no disponible.</span>
      <span className="text-xs text-zinc-600 max-w-md">
        El SimulationAgent (Claude Opus 4.7) puede recrear la escena a partir
        del informe pericial, los datos del caso y los specialists ya
        ejecutados.
      </span>
      {onGenerar && (
        <button
          onClick={onGenerar}
          disabled={generando}
          className="mt-2 px-4 py-2 rounded-md bg-[#C2E94B]/20 hover:bg-[#C2E94B]/30 disabled:opacity-50 text-[#C2E94B] border border-[#C2E94B]/40 text-xs font-mono uppercase tracking-wide transition"
        >
          {generando ? "Reconstruyendo escena…" : "✨ Generar simulación"}
        </button>
      )}
    </div>
  );
}
