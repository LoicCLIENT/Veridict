"use client";

import type { Infraccion } from "@/lib/api";
import { Scale } from "lucide-react";

interface RazonamientoLegalProps {
  infracciones: Infraccion[];
  veredicto?: {
    culpa_a: number;
    culpa_b: number;
    confidence: number;
  };
}

export function RazonamientoLegal({
  infracciones,
  veredicto,
}: RazonamientoLegalProps) {
  return (
    <div className="p-4 space-y-6">
      <h3 className="font-semibold flex items-center gap-2">
        <Scale className="w-4 h-4" />
        Razonamiento Legal
      </h3>

      {/* Veredicto */}
      {veredicto && (
        <div className="p-4 rounded-lg bg-secondary/50">
          <div className="text-sm text-muted-foreground mb-2">
            Atribucion de culpa
          </div>
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="text-xs text-muted-foreground">Vehiculo A</div>
              <div className="text-2xl font-bold">
                {Math.round(veredicto.culpa_a * 100)}%
              </div>
            </div>
            <div className="flex-1">
              <div className="text-xs text-muted-foreground">Vehiculo B</div>
              <div className="text-2xl font-bold">
                {Math.round(veredicto.culpa_b * 100)}%
              </div>
            </div>
          </div>
          <div className="mt-2 text-xs text-muted-foreground">
            Confianza: {Math.round(veredicto.confidence * 100)}%
          </div>
        </div>
      )}

      {/* Infracciones */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium">Infracciones detectadas</h4>
        {infracciones.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No se detectaron infracciones
          </p>
        ) : (
          infracciones.map((infraccion, index) => (
            <div
              key={index}
              className="p-3 rounded-lg border border-border bg-card"
            >
              <div className="flex items-center gap-2 mb-1">
                <span
                  className={`text-xs font-medium px-2 py-0.5 rounded ${
                    infraccion.vehiculo === "A"
                      ? "bg-blue-500/20 text-blue-400"
                      : "bg-orange-500/20 text-orange-400"
                  }`}
                >
                  Vehiculo {infraccion.vehiculo}
                </span>
                <span className="text-xs font-mono text-muted-foreground">
                  {infraccion.articulo}
                </span>
              </div>
              <p className="text-sm">{infraccion.descripcion}</p>
              <p className="text-xs text-muted-foreground mt-1">
                Fuente: {infraccion.fuente}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
