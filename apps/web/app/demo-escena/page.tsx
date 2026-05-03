"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { ArrowLeft, Play, Pause, RotateCcw, ChevronDown } from "lucide-react";
import AccidentScene2D, { AccidentSceneData } from "@/components/reconstruction/AccidentScene2D";

// Escena 1: Colisión lateral por cambio de carril
const escenaLateral: AccidentSceneData = {
  road: {
    type: "straight",
    lanes: 2,
    laneWidth: 3.5,
    speedLimit: 50
  },
  vehicleA: {
    trajectory: [
      { x: -10, y: -1.75, time: 0.0, speed: 67.0 },
      { x: -5, y: -1.75, time: 0.27, speed: 67.0 },
      { x: 0, y: -1.75, time: 0.54, speed: 67.0 },
      { x: 5, y: -1.75, time: 0.81, speed: 67.0 },
      { x: 10, y: -1.75, time: 1.08, speed: 67.0 },
      { x: 15, y: -1.75, time: 1.35, speed: 67.0 },
      { x: 20, y: -1.75, time: 1.62, speed: 67.0 },
      { x: 25, y: -1.75, time: 1.89, speed: 67.0 },
      { x: 27, y: -1.75, time: 2.0, speed: 67.0 },
      { x: 29, y: -1.75, time: 2.1, speed: 64.0 },
      { x: 31, y: -1.75, time: 2.2, speed: 61.0 },
      { x: 33, y: -1.75, time: 2.3, speed: 58.0 },
      { x: 35, y: -1.75, time: 2.4, speed: 55.0 },
      { x: 37, y: -1.75, time: 2.5, speed: 52.0 },
      { x: 38.5, y: -1.75, time: 2.6, speed: 49.0 },
      { x: 40, y: -1.75, time: 2.7, speed: 46.0 },
      { x: 41.2, y: -1.75, time: 2.8, speed: 43.0 },
      { x: 42.3, y: -1.75, time: 2.9, speed: 40.0 },
      { x: 43.2, y: -1.75, time: 3.0, speed: 37.0 },
      { x: 44, y: -1.75, time: 3.1, speed: 34.0 },
      { x: 44.7, y: -1.75, time: 3.2, speed: 31.0 },
      { x: 45.3, y: -1.75, time: 3.3, speed: 28.0 },
      { x: 45.8, y: -1.75, time: 3.4, speed: 25.0 },
      { x: 46.2, y: -1.75, time: 3.5, speed: 22.0 },
      { x: 46.5, y: -1.75, time: 3.6, speed: 19.0 },
      { x: 46.7, y: -1.75, time: 3.7, speed: 16.0 },
      { x: 42, y: -1.75, time: 4.0, speed: 15.0 },
    ],
    brakeStartTime: 2.0,
    brakeDistance: 12.5,
    initialSpeed: 67.0,
    impactSpeed: 15.0,
  },
  vehicleB: {
    trajectory: [
      { x: 5, y: 1.75, time: 0.0, speed: 55.0 },
      { x: 8, y: 1.75, time: 0.2, speed: 55.0 },
      { x: 11, y: 1.75, time: 0.4, speed: 55.0 },
      { x: 14, y: 1.6, time: 0.6, speed: 55.0 },
      { x: 17, y: 1.4, time: 0.8, speed: 55.0 },
      { x: 20, y: 1.1, time: 1.0, speed: 55.0 },
      { x: 23, y: 0.8, time: 1.2, speed: 55.0 },
      { x: 26, y: 0.5, time: 1.4, speed: 55.0 },
      { x: 29, y: 0.2, time: 1.6, speed: 55.0 },
      { x: 32, y: -0.1, time: 1.8, speed: 55.0 },
      { x: 35, y: -0.4, time: 2.0, speed: 55.0 },
      { x: 38, y: -0.7, time: 2.2, speed: 55.0 },
      { x: 41, y: -1.0, time: 2.4, speed: 55.0 },
      { x: 43, y: -1.2, time: 2.6, speed: 55.0 },
      { x: 45, y: -1.4, time: 2.8, speed: 55.0 },
      { x: 47, y: -1.6, time: 3.0, speed: 55.0 },
      { x: 49, y: -1.75, time: 3.1, speed: 52.0 },
      { x: 51, y: -1.75, time: 3.2, speed: 49.0 },
      { x: 52.5, y: -1.75, time: 3.3, speed: 46.0 },
      { x: 54, y: -1.75, time: 3.4, speed: 43.0 },
      { x: 55.2, y: -1.75, time: 3.5, speed: 40.0 },
      { x: 56.3, y: -1.75, time: 3.6, speed: 37.0 },
      { x: 57.2, y: -1.75, time: 3.7, speed: 34.0 },
      { x: 42, y: -1.75, time: 4.0, speed: 28.0 },
    ],
    brakeStartTime: 3.0,
    brakeDistance: 8.0,
    initialSpeed: 55.0,
    impactSpeed: 28.0,
  },
  impact: {
    x: 42,
    y: -1.75,
    time: 4.0,
    angle: 25,
    deltaV_A: 18,
    deltaV_B: 22,
  },
  metadata: {
    scaleMetersPerUnit: 1,
    weatherCondition: "Despejado",
    roadCondition: "Seco",
    visibility: "Buena",
  },
};

// Escena 2: Colisión por alcance
const escenaAlcance: AccidentSceneData = {
  road: {
    type: "straight",
    lanes: 2,
    laneWidth: 3.5,
    speedLimit: 60
  },
  vehicleA: {
    trajectory: [
      { x: -20, y: -1.75, time: 0.0, speed: 80.0 },
      { x: -10, y: -1.75, time: 0.45, speed: 80.0 },
      { x: 0, y: -1.75, time: 0.9, speed: 80.0 },
      { x: 10, y: -1.75, time: 1.35, speed: 80.0 },
      { x: 15, y: -1.75, time: 1.57, speed: 80.0 },
      { x: 18, y: -1.75, time: 1.7, speed: 75.0 },
      { x: 21, y: -1.75, time: 1.85, speed: 70.0 },
      { x: 24, y: -1.75, time: 2.0, speed: 65.0 },
      { x: 27, y: -1.75, time: 2.2, speed: 58.0 },
      { x: 30, y: -1.75, time: 2.4, speed: 51.0 },
      { x: 32, y: -1.75, time: 2.55, speed: 45.0 },
      { x: 34, y: -1.75, time: 2.7, speed: 39.0 },
      { x: 35.5, y: -1.75, time: 2.85, speed: 33.0 },
      { x: 36.5, y: -1.75, time: 3.0, speed: 27.0 },
      { x: 37, y: -1.75, time: 3.1, speed: 23.0 },
      { x: 40, y: -1.75, time: 3.5, speed: 23.0 },
    ],
    brakeStartTime: 1.5,
    brakeDistance: 35.0,
    initialSpeed: 80.0,
    impactSpeed: 23.0,
  },
  vehicleB: {
    trajectory: [
      { x: 20, y: -1.75, time: 0.0, speed: 25.0 },
      { x: 22, y: -1.75, time: 0.3, speed: 25.0 },
      { x: 24, y: -1.75, time: 0.6, speed: 25.0 },
      { x: 26, y: -1.75, time: 0.9, speed: 25.0 },
      { x: 28, y: -1.75, time: 1.2, speed: 25.0 },
      { x: 30, y: -1.75, time: 1.5, speed: 22.0 },
      { x: 32, y: -1.75, time: 1.8, speed: 18.0 },
      { x: 34, y: -1.75, time: 2.1, speed: 14.0 },
      { x: 35.5, y: -1.75, time: 2.4, speed: 10.0 },
      { x: 37, y: -1.75, time: 2.7, speed: 6.0 },
      { x: 38, y: -1.75, time: 3.0, speed: 3.0 },
      { x: 40, y: -1.75, time: 3.5, speed: 3.0 },
    ],
    brakeStartTime: 1.4,
    brakeDistance: 5.0,
    initialSpeed: 25.0,
    impactSpeed: 3.0,
  },
  impact: {
    x: 40,
    y: -1.75,
    time: 3.5,
    angle: 0,
    deltaV_A: 25,
    deltaV_B: 15,
  },
  metadata: {
    scaleMetersPerUnit: 1,
    weatherCondition: "Lluvia",
    roadCondition: "Mojado",
    visibility: "Reducida",
  },
};

// Escena 3: Atropello
const escenaAtropello: AccidentSceneData = {
  road: {
    type: "straight",
    lanes: 2,
    laneWidth: 3.5,
    speedLimit: 50
  },
  vehicleA: {
    trajectory: [
      { x: -15, y: -1.75, time: 0.0, speed: 48.0 },
      { x: -10, y: -1.75, time: 0.37, speed: 48.0 },
      { x: -5, y: -1.75, time: 0.75, speed: 48.0 },
      { x: 0, y: -1.75, time: 1.12, speed: 48.0 },
      { x: 5, y: -1.75, time: 1.5, speed: 48.0 },
      { x: 8, y: -1.75, time: 1.72, speed: 48.0 },
      { x: 10, y: -1.75, time: 1.87, speed: 45.0 },
      { x: 12, y: -1.75, time: 2.02, speed: 42.0 },
      { x: 14, y: -1.75, time: 2.17, speed: 38.0 },
      { x: 15.5, y: -1.75, time: 2.3, speed: 34.0 },
      { x: 17, y: -1.75, time: 2.45, speed: 30.0 },
      { x: 18, y: -1.75, time: 2.57, speed: 26.0 },
      { x: 19, y: -1.75, time: 2.7, speed: 22.0 },
      { x: 19.8, y: -1.75, time: 2.82, speed: 18.0 },
      { x: 20.5, y: -1.75, time: 2.95, speed: 14.0 },
      { x: 21, y: -1.75, time: 3.1, speed: 10.0 },
      { x: 20, y: -1.75, time: 3.5, speed: 10.0 },
    ],
    brakeStartTime: 1.8,
    brakeDistance: 10.0,
    initialSpeed: 48.0,
    impactSpeed: 10.0,
  },
  vehicleB: {
    trajectory: [
      { x: 20, y: 8, time: 0.0, speed: 5.0 },
      { x: 20, y: 7, time: 0.7, speed: 5.0 },
      { x: 20, y: 6, time: 1.4, speed: 5.0 },
      { x: 20, y: 5, time: 2.1, speed: 5.0 },
      { x: 20, y: 4, time: 2.8, speed: 5.0 },
      { x: 20, y: 3, time: 3.5, speed: 5.0 },
      { x: 20, y: 2, time: 4.2, speed: 5.0 },
      { x: 20, y: 1, time: 4.9, speed: 5.0 },
      { x: 20, y: 0, time: 5.6, speed: 5.0 },
      { x: 20, y: -1, time: 6.3, speed: 5.0 },
      { x: 20, y: -1.75, time: 3.5, speed: 0 },
    ],
    brakeStartTime: 3.5,
    brakeDistance: 0,
    initialSpeed: 5.0,
    impactSpeed: 0,
  },
  impact: {
    x: 20,
    y: -1.75,
    time: 3.5,
    angle: 90,
    deltaV_A: 15,
    deltaV_B: 48,
  },
  metadata: {
    scaleMetersPerUnit: 1,
    weatherCondition: "Despejado",
    roadCondition: "Seco",
    visibility: "Buena",
  },
};

const escenas = {
  lateral: {
    nombre: "Colision Lateral",
    descripcion: "Cambio de carril imprudente. Vehiculo B invade carril de A.",
    datos: escenaLateral,
  },
  alcance: {
    nombre: "Colision por Alcance",
    descripcion: "Vehiculo A no frena a tiempo. Calzada mojada.",
    datos: escenaAlcance,
  },
  atropello: {
    nombre: "Atropello de Peaton",
    descripcion: "Peaton cruza por paso de cebra.",
    datos: escenaAtropello,
  },
};

type EscenaKey = keyof typeof escenas;

export default function DemoEscenaPage() {
  const [escenaActual, setEscenaActual] = useState<EscenaKey>("lateral");
  const [key, setKey] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const animationRef = useRef<number | null>(null);

  const escena = escenas[escenaActual];

  // Animation loop
  useEffect(() => {
    if (!isPlaying) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      return;
    }

    const animate = () => {
      setCurrentTime(prev => {
        if (prev >= 100) {
          return 0; // Loop
        }
        return prev + 0.5; // Speed of animation
      });
      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying]);

  const reiniciar = () => {
    setCurrentTime(0);
    setIsPlaying(true);
    setKey(prev => prev + 1);
  };

  const cambiarEscena = (key: EscenaKey) => {
    setEscenaActual(key);
    setCurrentTime(0);
    setIsPlaying(true);
  };

  return (
    <div className="min-h-screen bg-[#0a0f0d] text-white p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-[#c2e94b] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Volver
        </Link>
        <div className="text-xs font-mono text-gray-500 uppercase tracking-widest">
          Demo · AccidentScene2D
        </div>
      </div>

      {/* Title */}
      <div className="text-center mb-6">
        <h1 className="text-2xl md:text-3xl font-bold mb-2">
          Visualizacion de Escenas Generadas
        </h1>
        <p className="text-gray-400 text-sm">
          Escenas parametrizadas generadas automaticamente desde datos del caso
        </p>
      </div>

      {/* Selector de escena */}
      <div className="flex flex-wrap justify-center gap-3 mb-6">
        {(Object.keys(escenas) as EscenaKey[]).map((escenaKey) => (
          <button
            key={escenaKey}
            onClick={() => cambiarEscena(escenaKey)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              escenaActual === escenaKey
                ? "bg-[#c2e94b] text-black"
                : "bg-gray-800 text-gray-300 hover:bg-gray-700"
            }`}
          >
            {escenas[escenaKey].nombre}
          </button>
        ))}
      </div>

      {/* Info de la escena */}
      <div className="max-w-4xl mx-auto mb-4">
        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h2 className="font-bold text-lg text-[#c2e94b]">{escena.nombre}</h2>
              <p className="text-gray-400 text-sm">{escena.descripcion}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="flex items-center gap-2 px-3 py-1.5 bg-[#c2e94b] hover:bg-[#d4f55d] text-black rounded text-sm transition-colors"
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                {isPlaying ? "Pausar" : "Reproducir"}
              </button>
              <button
                onClick={reiniciar}
                className="flex items-center gap-2 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                Reiniciar
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="max-w-4xl mx-auto mb-4">
        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
          <div className="flex items-center gap-4">
            <span className="text-xs text-gray-400 w-16">Tiempo:</span>
            <input
              type="range"
              min="0"
              max="100"
              value={currentTime}
              onChange={(e) => {
                setCurrentTime(Number(e.target.value));
                setIsPlaying(false);
              }}
              className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-[#c2e94b]"
            />
            <span className="text-xs text-gray-400 w-12 text-right">{Math.round(currentTime)}%</span>
          </div>
        </div>
      </div>

      {/* Visualizacion */}
      <div className="max-w-5xl mx-auto">
        <div className="bg-gray-900 rounded-xl border border-gray-700 overflow-hidden">
          <AccidentScene2D
            key={key}
            data={escena.datos}
            currentTime={currentTime}
            showTrajectories={true}
            showMeasurements={true}
            interactive={true}
          />
        </div>
      </div>

      {/* Datos tecnicos */}
      <div className="max-w-4xl mx-auto mt-6">
        <details className="bg-gray-800/50 rounded-lg border border-gray-700">
          <summary className="px-4 py-3 cursor-pointer flex items-center justify-between text-sm font-medium text-gray-300 hover:text-white">
            <span>Ver datos tecnicos (JSON)</span>
            <ChevronDown className="w-4 h-4" />
          </summary>
          <div className="px-4 pb-4">
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="text-[#c2e94b] font-mono mb-2">Vehiculo A</h4>
                <ul className="space-y-1 text-gray-400">
                  <li>Vel. inicial: <span className="text-white">{escena.datos.vehicleA.initialSpeed} km/h</span></li>
                  <li>Vel. impacto: <span className="text-white">{escena.datos.vehicleA.impactSpeed} km/h</span></li>
                  <li>Dist. frenado: <span className="text-white">{escena.datos.vehicleA.brakeDistance} m</span></li>
                  <li>Inicio frenada: <span className="text-white">{escena.datos.vehicleA.brakeStartTime} s</span></li>
                </ul>
              </div>
              <div>
                <h4 className="text-[#c2e94b] font-mono mb-2">Vehiculo B</h4>
                <ul className="space-y-1 text-gray-400">
                  <li>Vel. inicial: <span className="text-white">{escena.datos.vehicleB.initialSpeed} km/h</span></li>
                  <li>Vel. impacto: <span className="text-white">{escena.datos.vehicleB.impactSpeed} km/h</span></li>
                  <li>Dist. frenado: <span className="text-white">{escena.datos.vehicleB.brakeDistance} m</span></li>
                  <li>Inicio frenada: <span className="text-white">{escena.datos.vehicleB.brakeStartTime} s</span></li>
                </ul>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-700">
              <h4 className="text-[#c2e94b] font-mono mb-2">Impacto</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Posicion:</span>
                  <span className="text-white ml-2">({escena.datos.impact.x}, {escena.datos.impact.y})</span>
                </div>
                <div>
                  <span className="text-gray-400">Tiempo:</span>
                  <span className="text-white ml-2">{escena.datos.impact.time} s</span>
                </div>
                <div>
                  <span className="text-gray-400">Delta-V A:</span>
                  <span className="text-white ml-2">{escena.datos.impact.deltaV_A} km/h</span>
                </div>
                <div>
                  <span className="text-gray-400">Delta-V B:</span>
                  <span className="text-white ml-2">{escena.datos.impact.deltaV_B} km/h</span>
                </div>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-700">
              <h4 className="text-[#c2e94b] font-mono mb-2">Condiciones</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-400">
                <div>Clima: <span className="text-white">{escena.datos.metadata.weatherCondition}</span></div>
                <div>Calzada: <span className="text-white">{escena.datos.metadata.roadCondition}</span></div>
                <div>Visibilidad: <span className="text-white">{escena.datos.metadata.visibility}</span></div>
                <div>Carriles: <span className="text-white">{escena.datos.road.lanes}</span></div>
              </div>
            </div>
          </div>
        </details>
      </div>

      {/* Footer */}
      <div className="max-w-4xl mx-auto mt-8 text-center text-xs text-gray-500">
        <p>
          Escenas generadas automaticamente por el sistema de reconstruccion Veridict.
          <br />
          Los calculos fisicos (frenado, trayectorias, Delta-V) son deterministas basados en formulas reales.
        </p>
      </div>
    </div>
  );
}
