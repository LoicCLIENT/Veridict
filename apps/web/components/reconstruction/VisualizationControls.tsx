"use client";

import { useState } from "react";
import {
  Eye,
  EyeOff,
  Grid3X3,
  Route,
  Ruler,
  Target,
  Gauge,
  Car,
  Truck,
  Bike,
  Palette,
  RotateCcw,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Maximize2,
  Focus,
  ChevronDown,
  Box,
  Layers,
} from "lucide-react";

export interface VisualizationSettings {
  // View
  viewMode: "2d-top" | "2d-isometric";

  // Display toggles
  showGrid: boolean;
  showMeasurements: boolean;
  showTrajectories: boolean;
  showBrakeMarks: boolean;
  showSpeedLabels: boolean;
  showImpactZone: boolean;
  showDistanceLines: boolean;

  // Vehicle customization
  vehicleA: {
    type: "sedan" | "suv" | "van" | "truck" | "motorcycle";
    color: string;
  };
  vehicleB: {
    type: "sedan" | "suv" | "van" | "truck" | "motorcycle";
    color: string;
  };

  // Playback
  playbackSpeed: 0.25 | 0.5 | 1 | 2;
  loop: boolean;
}

interface VisualizationControlsProps {
  settings: VisualizationSettings;
  onSettingsChange: (settings: VisualizationSettings) => void;
  currentTime: number;
  isPlaying: boolean;
  onPlayPause: () => void;
  onTimeChange: (time: number) => void;
  onReset: () => void;
  onCenterOn: (target: "A" | "B" | "impact" | "overview") => void;
}

const VEHICLE_TYPES = [
  { id: "sedan", label: "Sedan", icon: Car },
  { id: "suv", label: "SUV", icon: Car },
  { id: "van", label: "Van", icon: Truck },
  { id: "truck", label: "Truck", icon: Truck },
  { id: "motorcycle", label: "Motorcycle", icon: Bike },
] as const;

const VEHICLE_COLORS = [
  { id: "#3B82F6", label: "Blue" },
  { id: "#EF4444", label: "Red" },
  { id: "#10B981", label: "Green" },
  { id: "#F59E0B", label: "Orange" },
  { id: "#8B5CF6", label: "Purple" },
  { id: "#6B7280", label: "Gray" },
  { id: "#FFFFFF", label: "White" },
  { id: "#1F2937", label: "Black" },
];

const PLAYBACK_SPEEDS = [
  { value: 0.25, label: "0.25x" },
  { value: 0.5, label: "0.5x" },
  { value: 1, label: "1x" },
  { value: 2, label: "2x" },
] as const;

export function VisualizationControls({
  settings,
  onSettingsChange,
  currentTime,
  isPlaying,
  onPlayPause,
  onTimeChange,
  onReset,
  onCenterOn,
}: VisualizationControlsProps) {
  const [expandedPanel, setExpandedPanel] = useState<string | null>(null);

  const updateSetting = <K extends keyof VisualizationSettings>(
    key: K,
    value: VisualizationSettings[K]
  ) => {
    onSettingsChange({ ...settings, [key]: value });
  };

  const updateVehicle = (
    vehicle: "vehicleA" | "vehicleB",
    updates: Partial<VisualizationSettings["vehicleA"]>
  ) => {
    onSettingsChange({
      ...settings,
      [vehicle]: { ...settings[vehicle], ...updates },
    });
  };

  const togglePanel = (panel: string) => {
    setExpandedPanel(expandedPanel === panel ? null : panel);
  };

  return (
    <div className="flex flex-col gap-3">
      {/* Top toolbar */}
      <div className="flex items-center justify-between gap-2 p-2 bg-[#0d110d] rounded-lg border border-white/[0.06]">
        {/* View mode */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => updateSetting("viewMode", "2d-top")}
            className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
              settings.viewMode === "2d-top"
                ? "bg-[#C2E94B]/20 text-[#C2E94B]"
                : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
            }`}
          >
            <span className="flex items-center gap-1.5">
              <Layers size={14} />
              2D Top
            </span>
          </button>
          <button
            onClick={() => updateSetting("viewMode", "2d-isometric")}
            className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
              settings.viewMode === "2d-isometric"
                ? "bg-[#C2E94B]/20 text-[#C2E94B]"
                : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
            }`}
          >
            <span className="flex items-center gap-1.5">
              <Box size={14} />
              Isometric
            </span>
          </button>
        </div>

        {/* Quick toggles */}
        <div className="flex items-center gap-1">
          <ToggleButton
            active={settings.showGrid}
            onClick={() => updateSetting("showGrid", !settings.showGrid)}
            icon={<Grid3X3 size={14} />}
            tooltip="Grid"
          />
          <ToggleButton
            active={settings.showTrajectories}
            onClick={() => updateSetting("showTrajectories", !settings.showTrajectories)}
            icon={<Route size={14} />}
            tooltip="Trajectories"
          />
          <ToggleButton
            active={settings.showMeasurements}
            onClick={() => updateSetting("showMeasurements", !settings.showMeasurements)}
            icon={<Ruler size={14} />}
            tooltip="Measurements"
          />
          <ToggleButton
            active={settings.showSpeedLabels}
            onClick={() => updateSetting("showSpeedLabels", !settings.showSpeedLabels)}
            icon={<Gauge size={14} />}
            tooltip="Speeds"
          />
          <ToggleButton
            active={settings.showImpactZone}
            onClick={() => updateSetting("showImpactZone", !settings.showImpactZone)}
            icon={<Target size={14} />}
            tooltip="Impact zone"
          />
        </div>

        {/* Camera presets */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => onCenterOn("overview")}
            className="p-1.5 rounded text-zinc-500 hover:text-zinc-300 hover:bg-white/5 transition-colors"
            title="Overview"
          >
            <Maximize2 size={14} />
          </button>
          <button
            onClick={() => onCenterOn("A")}
            className="px-2 py-1 rounded text-xs font-mono text-blue-400 hover:bg-blue-500/10 transition-colors"
            title="Center on A"
          >
            A
          </button>
          <button
            onClick={() => onCenterOn("B")}
            className="px-2 py-1 rounded text-xs font-mono text-orange-400 hover:bg-orange-500/10 transition-colors"
            title="Center on B"
          >
            B
          </button>
          <button
            onClick={() => onCenterOn("impact")}
            className="p-1.5 rounded text-red-400 hover:bg-red-500/10 transition-colors"
            title="Go to impact"
          >
            <Focus size={14} />
          </button>
        </div>
      </div>

      {/* Expandable panels */}
      <div className="flex gap-2">
        {/* Vehicle A panel */}
        <div className="flex-1">
          <button
            onClick={() => togglePanel("vehicleA")}
            className="w-full flex items-center justify-between p-2 bg-[#0d110d] rounded-lg border border-blue-500/20 hover:border-blue-500/40 transition-colors"
          >
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: settings.vehicleA.color }} />
              <span className="text-xs font-medium text-blue-400">Vehicle A</span>
            </div>
            <ChevronDown
              size={14}
              className={`text-zinc-500 transition-transform ${expandedPanel === "vehicleA" ? "rotate-180" : ""}`}
            />
          </button>
          {expandedPanel === "vehicleA" && (
            <VehicleEditor
              vehicle={settings.vehicleA}
              onChange={(updates) => updateVehicle("vehicleA", updates)}
            />
          )}
        </div>

        {/* Vehicle B panel */}
        <div className="flex-1">
          <button
            onClick={() => togglePanel("vehicleB")}
            className="w-full flex items-center justify-between p-2 bg-[#0d110d] rounded-lg border border-orange-500/20 hover:border-orange-500/40 transition-colors"
          >
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: settings.vehicleB.color }} />
              <span className="text-xs font-medium text-orange-400">Vehicle B</span>
            </div>
            <ChevronDown
              size={14}
              className={`text-zinc-500 transition-transform ${expandedPanel === "vehicleB" ? "rotate-180" : ""}`}
            />
          </button>
          {expandedPanel === "vehicleB" && (
            <VehicleEditor
              vehicle={settings.vehicleB}
              onChange={(updates) => updateVehicle("vehicleB", updates)}
            />
          )}
        </div>
      </div>

      {/* Timeline controls */}
      <div className="p-3 bg-[#0d110d] rounded-lg border border-white/[0.06]">
        <div className="flex items-center gap-3">
          {/* Playback controls */}
          <div className="flex items-center gap-1">
            <button
              onClick={onReset}
              className="p-1.5 rounded text-zinc-500 hover:text-zinc-300 hover:bg-white/5 transition-colors"
              title="Reset"
            >
              <RotateCcw size={14} />
            </button>
            <button
              onClick={() => onTimeChange(Math.max(0, currentTime - 10))}
              className="p-1.5 rounded text-zinc-500 hover:text-zinc-300 hover:bg-white/5 transition-colors"
              title="-10%"
            >
              <SkipBack size={14} />
            </button>
            <button
              onClick={onPlayPause}
              className={`p-2 rounded transition-colors ${
                isPlaying
                  ? "bg-red-500/20 text-red-400 hover:bg-red-500/30"
                  : "bg-[#C2E94B]/20 text-[#C2E94B] hover:bg-[#C2E94B]/30"
              }`}
            >
              {isPlaying ? <Pause size={16} /> : <Play size={16} />}
            </button>
            <button
              onClick={() => onTimeChange(Math.min(100, currentTime + 10))}
              className="p-1.5 rounded text-zinc-500 hover:text-zinc-300 hover:bg-white/5 transition-colors"
              title="+10%"
            >
              <SkipForward size={14} />
            </button>
          </div>

          {/* Timeline slider */}
          <div className="flex-1 flex items-center gap-3">
            <input
              type="range"
              min="0"
              max="100"
              value={currentTime}
              onChange={(e) => onTimeChange(Number(e.target.value))}
              className="flex-1 h-1.5 bg-zinc-800 rounded-full appearance-none cursor-pointer
                [&::-webkit-slider-thumb]:appearance-none
                [&::-webkit-slider-thumb]:w-3
                [&::-webkit-slider-thumb]:h-3
                [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:bg-[#C2E94B]
                [&::-webkit-slider-thumb]:shadow-[0_0_8px_rgba(194,233,75,0.5)]
                [&::-webkit-slider-thumb]:transition-shadow
                [&::-webkit-slider-thumb]:hover:shadow-[0_0_12px_rgba(194,233,75,0.8)]"
            />
            <span className="text-xs font-mono text-zinc-400 min-w-[36px] text-right">
              {currentTime}%
            </span>
          </div>

          {/* Speed control */}
          <div className="flex items-center gap-1 border-l border-white/[0.06] pl-3">
            {PLAYBACK_SPEEDS.map((speed) => (
              <button
                key={speed.value}
                onClick={() => updateSetting("playbackSpeed", speed.value)}
                className={`px-2 py-1 rounded text-[10px] font-mono transition-colors ${
                  settings.playbackSpeed === speed.value
                    ? "bg-[#C2E94B]/20 text-[#C2E94B]"
                    : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
                }`}
              >
                {speed.label}
              </button>
            ))}
          </div>

          {/* Loop toggle */}
          <button
            onClick={() => updateSetting("loop", !settings.loop)}
            className={`p-1.5 rounded transition-colors ${
              settings.loop
                ? "bg-[#C2E94B]/20 text-[#C2E94B]"
                : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
            }`}
            title="Loop"
          >
            <RotateCcw size={14} />
          </button>
        </div>

        {/* Timeline markers */}
        <div className="mt-2 flex items-center justify-between text-[10px] font-mono text-zinc-600">
          <span>0s - Start</span>
          <span className="text-yellow-500">Braking</span>
          <span className="text-red-400">Impact</span>
          <span>End</span>
        </div>
      </div>
    </div>
  );
}

function ToggleButton({
  active,
  onClick,
  icon,
  tooltip,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  tooltip: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`p-1.5 rounded transition-colors ${
        active
          ? "bg-[#C2E94B]/20 text-[#C2E94B]"
          : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
      }`}
      title={tooltip}
    >
      {icon}
    </button>
  );
}

function VehicleEditor({
  vehicle,
  onChange,
}: {
  vehicle: VisualizationSettings["vehicleA"];
  onChange: (updates: Partial<VisualizationSettings["vehicleA"]>) => void;
}) {
  return (
    <div className="mt-2 p-3 bg-[#0a0a0a] rounded-lg border border-white/[0.04] space-y-3">
      {/* Vehicle type */}
      <div>
        <label className="text-[10px] font-medium text-zinc-500 uppercase tracking-wide mb-1.5 block">
          Vehicle type
        </label>
        <div className="flex flex-wrap gap-1">
          {VEHICLE_TYPES.map((type) => {
            const Icon = type.icon;
            return (
              <button
                key={type.id}
                onClick={() => onChange({ type: type.id })}
                className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs transition-colors ${
                  vehicle.type === type.id
                    ? "bg-white/10 text-white"
                    : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
                }`}
              >
                <Icon size={12} />
                {type.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Vehicle color */}
      <div>
        <label className="text-[10px] font-medium text-zinc-500 uppercase tracking-wide mb-1.5 block">
          Color
        </label>
        <div className="flex gap-1">
          {VEHICLE_COLORS.map((color) => (
            <button
              key={color.id}
              onClick={() => onChange({ color: color.id })}
              className={`w-6 h-6 rounded border-2 transition-all ${
                vehicle.color === color.id
                  ? "border-[#C2E94B] scale-110"
                  : "border-transparent hover:border-white/30"
              }`}
              style={{ backgroundColor: color.id }}
              title={color.label}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export const defaultVisualizationSettings: VisualizationSettings = {
  viewMode: "2d-top",
  showGrid: true,
  showMeasurements: true,
  showTrajectories: true,
  showBrakeMarks: true,
  showSpeedLabels: true,
  showImpactZone: true,
  showDistanceLines: true,
  vehicleA: {
    type: "sedan",
    color: "#3B82F6",
  },
  vehicleB: {
    type: "sedan",
    color: "#F97316",
  },
  playbackSpeed: 1,
  loop: false,
};
