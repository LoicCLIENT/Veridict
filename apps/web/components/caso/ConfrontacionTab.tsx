"use client";

import type {
  Vehiculo,
  ContrastVersiones,
  CompatibilidadVersiones,
  CalculoFisico,
  VerificacionAdversarial,
} from "@/lib/api";
import { Shield, CheckCircle2, XCircle, User, Car, Scale, Zap, AlertTriangle } from "lucide-react";

interface ConfrontacionTabProps {
  vehiculos: Vehiculo[];
  contrastes?: ContrastVersiones[];
  compatibilidad?: CompatibilidadVersiones;
  calculos?: CalculoFisico[];
  adversarial?: VerificacionAdversarial;
}

function VersionPanel({
  vehiculo,
  contraste,
  compatible,
  side,
}: {
  vehiculo?: Vehiculo;
  contraste?: ContrastVersiones;
  compatible?: boolean;
  side: "A" | "B";
}) {
  const colorBg = side === "A" ? "bg-blue-500/5 border-blue-500/20" : "bg-orange-500/5 border-orange-500/20";
  const colorText = side === "A" ? "text-blue-400" : "text-orange-400";
  const compatNotKnown = compatible === undefined;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
          side === "A" ? "bg-blue-500/20 border border-blue-500/40" : "bg-orange-500/20 border border-orange-500/40"
        }`}>
          <Car className={`w-6 h-6 ${colorText}`} />
        </div>
        <div>
          <h3 className="font-semibold text-veridict-white">Vehicle {side}</h3>
          <p className="text-xs text-veridict-gray">
            {vehiculo?.modelo || "—"} · {vehiculo?.matricula || "—"}
          </p>
        </div>
      </div>

      <div className={`p-4 rounded-lg border ${colorBg}`}>
        <div className="flex items-center gap-2 mb-2">
          <User className={`w-4 h-4 ${colorText}`} />
          <span className={`text-xs font-medium ${colorText}`}>STATEMENT</span>
        </div>
        <p className="text-sm text-veridict-white italic">
          {vehiculo?.version_conductor
            ? `"${vehiculo.version_conductor}"`
            : "No statement recorded."}
        </p>
      </div>

      {contraste && (
        <div className="p-4 rounded-lg bg-veridict-green-800 border border-veridict-green-600 space-y-2">
          <div className="text-xs font-medium text-veridict-gray flex items-center gap-2">
            <Zap className="w-3 h-3" />
            TECHNICAL CONTRAST
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <div className="text-xs text-veridict-gray">Stated</div>
              <div className="font-mono text-veridict-white">
                {contraste.velocidad_declarada_kmh != null
                  ? `${contraste.velocidad_declarada_kmh.toFixed(1)} km/h`
                  : "—"}
              </div>
            </div>
            <div>
              <div className="text-xs text-veridict-gray">Calculated</div>
              <div className="font-mono text-veridict-lime">
                {contraste.velocidad_calculada_kmh != null
                  ? `${contraste.velocidad_calculada_kmh.toFixed(1)} km/h`
                  : "—"}
              </div>
            </div>
          </div>
          <p className="text-xs text-veridict-gray">{contraste.observacion}</p>
        </div>
      )}

      <div
        className={`p-3 rounded-lg flex items-center gap-2 border ${
          compatNotKnown
            ? "bg-veridict-gray/10 border-veridict-gray/30 text-veridict-gray"
            : compatible
            ? "bg-veridict-lime/10 border-veridict-lime/30 text-veridict-lime"
            : "bg-veridict-error/10 border-veridict-error/30 text-veridict-error"
        }`}
      >
        {compatNotKnown ? (
          <span className="text-sm">Compatibility not determined</span>
        ) : compatible ? (
          <>
            <CheckCircle2 className="w-4 h-4" />
            <span className="text-sm font-medium">Version compatible with physical evidence</span>
          </>
        ) : (
          <>
            <XCircle className="w-4 h-4" />
            <span className="text-sm font-medium">Version incompatible with physical evidence</span>
          </>
        )}
      </div>
    </div>
  );
}

export default function ConfrontacionTab({
  vehiculos,
  contrastes,
  compatibilidad,
  calculos,
  adversarial,
}: ConfrontacionTabProps) {
  const vehA = vehiculos.find((v) => v.id === "A");
  const vehB = vehiculos.find((v) => v.id === "B");
  const contrasteA = contrastes?.find((c) => c.vehiculo_id === "A");
  const contrasteB = contrastes?.find((c) => c.vehiculo_id === "B");

  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="text-center mb-6">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-veridict-error/10 border border-veridict-error/30 mb-3">
          <Shield className="w-5 h-5 text-veridict-error" />
          <span className="text-sm font-medium text-veridict-error">
            Devil&apos;s Advocate Analysis
          </span>
        </div>
        <h2 className="text-2xl font-bold text-veridict-white mb-1">Version Confrontation</h2>
        <p className="text-veridict-gray text-sm max-w-xl mx-auto">
          Driver statements contrasted against objective physical evidence.
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <VersionPanel vehiculo={vehA} contraste={contrasteA} compatible={compatibilidad?.a} side="A" />

        <div className="space-y-3">
          <div className="text-center mb-2">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-veridict-lime/10 border border-veridict-lime/30">
              <Scale className="w-4 h-4 text-veridict-lime" />
              <span className="text-xs font-medium text-veridict-lime">OBJECTIVE EVIDENCE</span>
            </div>
          </div>

          {(calculos ?? []).slice(0, 6).map((c, idx) => (
            <div
              key={idx}
              className="p-3 rounded-lg bg-veridict-green-800 border border-veridict-green-600"
            >
              <div className="text-xs text-veridict-gray mb-0.5">{c.nombre}</div>
              <div className="text-lg font-mono text-veridict-lime">
                {c.valor.toFixed(2)}
                <span className="text-xs text-veridict-gray ml-1">{c.unidad}</span>
              </div>
              <p className="text-xs text-veridict-gray mt-1">{c.justificacion}</p>
            </div>
          ))}

          {compatibilidad && (
            <div className="p-3 rounded-lg bg-veridict-green-800 border border-veridict-green-600">
              <div className="text-xs text-veridict-gray mb-1">Compatibility justification</div>
              <p className="text-xs text-veridict-white">{compatibilidad.justificacion}</p>
            </div>
          )}

          {adversarial && (
            <div
              className={`p-3 rounded-lg border ${
                adversarial.passed
                  ? "bg-veridict-lime/10 border-veridict-lime/30"
                  : "bg-veridict-error/10 border-veridict-error/30"
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                {adversarial.passed ? (
                  <CheckCircle2 className="w-4 h-4 text-veridict-lime" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-veridict-error" />
                )}
                <span
                  className={`text-xs font-medium ${
                    adversarial.passed ? "text-veridict-lime" : "text-veridict-error"
                  }`}
                >
                  {adversarial.passed
                    ? "Adversarial verification passed"
                    : `${adversarial.failures.length} failures detected`}
                </span>
              </div>
              {!adversarial.passed && (
                <ul className="text-xs text-veridict-error/80 list-disc list-inside space-y-0.5">
                  {adversarial.failures.map((f, i) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>

        <VersionPanel vehiculo={vehB} contraste={contrasteB} compatible={compatibilidad?.b} side="B" />
      </div>
    </div>
  );
}
