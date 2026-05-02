"use client";

import type { Infraccion, Veredicto, NexoCausal } from "@/lib/api";
import { Scale, AlertTriangle, GitBranch } from "lucide-react";

interface RazonamientoLegalProps {
  infracciones: Infraccion[];
  veredicto?: Veredicto;
}

const gravedadColor: Record<string, string> = {
  muy_grave: "bg-red-500/20 text-red-400 border-red-500/40",
  grave: "bg-orange-500/20 text-orange-400 border-orange-500/40",
  leve: "bg-yellow-500/20 text-yellow-400 border-yellow-500/40",
};

const nexoColor: Record<string, string> = {
  causa_eficiente: "bg-red-500/10 text-red-400 border-red-500/30",
  concurrente: "bg-orange-500/10 text-orange-400 border-orange-500/30",
  sin_nexo: "bg-veridict-gray/10 text-veridict-gray border-veridict-gray/30",
};

const nexoLabel: Record<string, string> = {
  causa_eficiente: "Causa eficiente",
  concurrente: "Concurrente",
  sin_nexo: "Sin nexo",
};

export function RazonamientoLegal({
  infracciones,
  veredicto,
}: RazonamientoLegalProps) {
  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      <h3 className="font-semibold flex items-center gap-2 text-veridict-white text-xl">
        <Scale className="w-5 h-5 text-veridict-lime" />
        Razonamiento Legal
      </h3>

      {/* Veredicto + razonamiento */}
      {veredicto && (
        <div className="p-4 rounded-lg bg-veridict-green-800 border border-veridict-green-600 space-y-3">
          <div className="text-sm text-veridict-gray">Atribución de culpa</div>
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="text-xs text-blue-400">Vehículo A</div>
              <div className="text-3xl font-bold text-blue-400">
                {Math.round(veredicto.culpa_a * 100)}%
              </div>
            </div>
            <div className="flex-1">
              <div className="text-xs text-orange-400">Vehículo B</div>
              <div className="text-3xl font-bold text-orange-400">
                {Math.round(veredicto.culpa_b * 100)}%
              </div>
            </div>
            <div className="flex-1 text-right">
              <div className="text-xs text-veridict-gray">Confianza</div>
              <div className="text-2xl font-mono text-veridict-lime">
                {Math.round(veredicto.confidence * 100)}%
              </div>
            </div>
          </div>

          {veredicto.advertencia_personal && (
            <div className="flex items-start gap-2 p-3 rounded bg-yellow-500/10 border border-yellow-500/30">
              <AlertTriangle className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
              <div className="text-xs text-yellow-300">
                <strong>Regla 100/100 TS:</strong> daños personales — la culpa civil puede no
                redistribuirse aun habiendo concurrencia. Revisión humana recomendada.
              </div>
            </div>
          )}

          {veredicto.razonamiento && (
            <div>
              <div className="text-xs text-veridict-gray mb-1">Razonamiento técnico-jurídico</div>
              <p className="text-sm text-veridict-white whitespace-pre-wrap leading-relaxed">
                {veredicto.razonamiento}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Nexo causal */}
      {veredicto?.nexo_causal && veredicto.nexo_causal.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-veridict-gray flex items-center gap-2">
            <GitBranch className="w-4 h-4" />
            Nexo causal por infracción
          </h4>
          <div className="space-y-2">
            {veredicto.nexo_causal.map((n: NexoCausal, idx: number) => (
              <div
                key={idx}
                className="p-3 rounded-lg border border-veridict-green-600 bg-veridict-green-800"
              >
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded ${
                      n.vehiculo === "A"
                        ? "bg-blue-500/20 text-blue-400"
                        : "bg-orange-500/20 text-orange-400"
                    }`}
                  >
                    Vehículo {n.vehiculo}
                  </span>
                  <span className="text-xs font-mono text-veridict-gray">{n.articulo}</span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded border ${
                      gravedadColor[n.gravedad] ?? "bg-veridict-gray/20 text-veridict-gray"
                    }`}
                  >
                    {n.gravedad}
                  </span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded border ${
                      nexoColor[n.nexo] ?? "bg-veridict-gray/20"
                    }`}
                  >
                    {nexoLabel[n.nexo] ?? n.nexo}
                  </span>
                </div>
                <p className="text-sm text-veridict-white">{n.justificacion}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Infracciones */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-veridict-gray">Infracciones detectadas</h4>
        {infracciones.length === 0 ? (
          <p className="text-sm text-veridict-gray">No se detectaron infracciones.</p>
        ) : (
          infracciones.map((infraccion, index) => (
            <div
              key={index}
              className="p-3 rounded-lg border border-veridict-green-600 bg-veridict-green-800"
            >
              <div className="flex items-center gap-2 mb-1">
                <span
                  className={`text-xs font-medium px-2 py-0.5 rounded ${
                    infraccion.vehiculo === "A"
                      ? "bg-blue-500/20 text-blue-400"
                      : "bg-orange-500/20 text-orange-400"
                  }`}
                >
                  Vehículo {infraccion.vehiculo}
                </span>
                <span className="text-xs font-mono text-veridict-gray">
                  {infraccion.articulo}
                </span>
              </div>
              <p className="text-sm text-veridict-white">{infraccion.descripcion}</p>
              <p className="text-xs text-veridict-gray mt-1">Fuente: {infraccion.fuente}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
