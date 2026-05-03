"use client";

import type { Vehiculo } from "@/lib/api";
import { Car, Gauge, ShieldCheck, Compass } from "lucide-react";

interface Props {
  vehiculos: Vehiculo[];
}

function Field({ label, value, mono = true }: { label: string; value: React.ReactNode; mono?: boolean }) {
  return (
    <div>
      <div className="text-xs text-veridict-gray">{label}</div>
      <div className={`text-sm text-veridict-white ${mono ? "font-mono" : ""}`}>
        {value === undefined || value === null || value === "" ? "—" : value}
      </div>
    </div>
  );
}

export function VehiculosPanel({ vehiculos }: Props) {
  if (!vehiculos || vehiculos.length === 0) {
    return (
      <div className="p-6 text-center text-veridict-gray text-sm">
        No vehicles registered.
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4 overflow-y-auto h-full">
      {vehiculos.map((v) => {
        const accent = v.id === "A" ? "blue" : "orange";
        return (
          <div
            key={v.id}
            className="p-4 rounded-lg bg-veridict-green-800 border border-veridict-green-600 space-y-4"
          >
            <div className="flex items-center gap-3">
              <div
                className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  accent === "blue"
                    ? "bg-blue-500/20 border border-blue-500/40 text-blue-400"
                    : "bg-orange-500/20 border border-orange-500/40 text-orange-400"
                }`}
              >
                <Car className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-veridict-white">Vehicle {v.id}</h4>
                <p className="text-xs text-veridict-gray">
                  {v.modelo || "Unknown model"} · {v.matricula || "—"}
                </p>
              </div>
            </div>

            {/* Identificación / masa */}
            <div className="grid md:grid-cols-4 gap-3">
              <Field label="Mass" value={v.masa_kg ? `${v.masa_kg} kg` : null} />
              <Field
                label="Stiffness coef. A"
                value={v.coef_rigidez_a ? `${v.coef_rigidez_a} kPa` : null}
              />
              <Field
                label="Stiffness coef. B"
                value={v.coef_rigidez_b ? `${v.coef_rigidez_b} kPa/m` : null}
              />
              <Field label="Damage width" value={v.ancho_zona_danada_cm ? `${v.ancho_zona_danada_cm} cm` : null} />
            </div>

            {/* Mediciones C1-C6 */}
            <div>
              <div className="flex items-center gap-2 text-xs text-veridict-gray mb-1">
                <Gauge className="w-3 h-3" />
                Measurements C1–C6 (CRASH3, cm)
              </div>
              <div className="grid grid-cols-6 gap-1">
                {(v.mediciones_C ?? []).map((c, i) => (
                  <div
                    key={i}
                    className="text-center text-xs font-mono p-1 rounded bg-veridict-green-700 text-veridict-white"
                  >
                    {c.toFixed(1)}
                  </div>
                ))}
              </div>
            </div>

            {/* Cinemática */}
            <div className="grid md:grid-cols-4 gap-3">
              <Field
                label="Skid length"
                value={v.longitud_frenada_m != null ? `${v.longitud_frenada_m} m` : null}
              />
              <Field
                label="Post-impact marks"
                value={
                  v.longitud_huellas_post_impacto_m != null
                    ? `${v.longitud_huellas_post_impacto_m} m`
                    : null
                }
              />
              <Field
                label="EDR speed"
                value={v.edr_velocidad_kmh != null ? `${v.edr_velocidad_kmh} km/h` : null}
              />
              <Field
                label="Approach angle"
                value={v.angulo_aproximacion_deg != null ? `${v.angulo_aproximacion_deg}°` : null}
              />
            </div>

            {/* Posición y airbag */}
            <div className="grid md:grid-cols-3 gap-3">
              <Field
                label="Final position (x,y) m"
                value={
                  v.posicion_final
                    ? `(${v.posicion_final[0].toFixed(2)}, ${v.posicion_final[1].toFixed(2)})`
                    : null
                }
              />
              <Field
                label="Airbag"
                value={
                  v.airbag_desplegado == null
                    ? null
                    : v.airbag_desplegado
                    ? "Deployed"
                    : "Not deployed"
                }
              />
              <Field
                label="Compass"
                value={
                  v.angulo_aproximacion_deg != null ? (
                    <span className="inline-flex items-center gap-1">
                      <Compass className="w-3 h-3" /> {v.angulo_aproximacion_deg}°
                    </span>
                  ) : null
                }
                mono={false}
              />
            </div>

            {/* Declaración */}
            {v.version_conductor && (
              <div className="p-3 rounded bg-veridict-green-700/40 border border-veridict-green-600">
                <div className="text-xs text-veridict-gray flex items-center gap-1 mb-1">
                  <ShieldCheck className="w-3 h-3" />
                  Driver statement
                </div>
                <p className="text-sm text-veridict-white italic">&quot;{v.version_conductor}&quot;</p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
