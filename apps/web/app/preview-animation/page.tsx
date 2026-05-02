"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import CrashReconstruction from "@/components/CrashReconstruction";

export default function PreviewAnimationPage() {
  return (
    <div className="min-h-[calc(100vh-80px)] py-10">
      {/* Header bar */}
      <div className="flex items-center justify-between mb-8">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-veridict-gray hover:text-veridict-lime transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Volver a la landing
        </Link>
        <div className="text-xs font-mono text-veridict-gray uppercase tracking-widest">
          Preview · Crash Reconstruction
        </div>
      </div>

      {/* Title */}
      <div className="text-center mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-veridict-white mb-3">
          Animación de reconstrucción forense
        </h1>
        <p className="text-veridict-gray max-w-2xl mx-auto">
          Aproximación → impacto → caos → reconstrucción inversa → dictamen
          forense. La animación se repite en bucle (~9 s por ciclo).
        </p>
      </div>

      {/* Animation stage */}
      <div className="relative rounded-xl overflow-hidden border border-veridict-green-600 bg-gradient-to-br from-veridict-green-900 via-[#162720] to-veridict-green-800 shadow-lg">
        {/* subtle radial glow */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(194,233,75,0.06)_0%,_transparent_70%)] pointer-events-none" />
        <div className="relative aspect-[2/1]">
          <CrashReconstruction className="absolute inset-0" />
        </div>
      </div>

      {/* Phase legend */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-6">
        <PhaseChip n="1" name="Aproximación" desc="Trayectoria + faros" duration="2.4 s" />
        <PhaseChip n="2" name="Impacto" desc="Flash + sacudida" duration="0.45 s" />
        <PhaseChip n="3" name="Caos" desc="Restos + deformación" duration="1.3 s" />
        <PhaseChip n="4" name="Reconstrucción" desc="Tiempo inverso + scan" duration="1.9 s" />
        <PhaseChip n="5" name="Dictamen" desc="Trayectorias + CRASH3" duration="2.4 s" />
      </div>

      <div className="mt-10 p-5 rounded-md border border-veridict-green-600 bg-veridict-green-800/40 text-sm text-veridict-gray">
        <span className="text-veridict-lime font-mono mr-2">i</span>
        ¿Te gusta? Dame feedback (más rápido / más lento, otros colores, otra
        cámara, sin texto, etc.) y la pulimos antes de meterla en el hero de la
        landing.
      </div>
    </div>
  );
}

function PhaseChip({
  n,
  name,
  desc,
  duration,
}: {
  n: string;
  name: string;
  desc: string;
  duration: string;
}) {
  return (
    <div className="rounded-md border border-veridict-green-600 bg-veridict-green-800/40 p-3">
      <div className="flex items-center gap-2 mb-1">
        <span className="w-5 h-5 rounded-full bg-veridict-lime/15 text-veridict-lime text-xs font-mono flex items-center justify-center">
          {n}
        </span>
        <span className="text-veridict-white text-sm font-semibold">
          {name}
        </span>
      </div>
      <div className="text-xs text-veridict-gray">{desc}</div>
      <div className="text-xs font-mono text-veridict-lime/70 mt-1">
        {duration}
      </div>
    </div>
  );
}
