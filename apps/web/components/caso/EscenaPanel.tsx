"use client";

import type { EscenaAccidente, HuellaCalzada, DanoSecundario } from "@/lib/api";
import { Footprints, AlertOctagon, Eye, Compass } from "lucide-react";

interface Props {
  escena?: EscenaAccidente | null;
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <div className="text-xs text-veridict-gray">{label}</div>
      <div className="text-sm text-veridict-white font-mono">
        {value === undefined || value === null || value === "" ? "—" : value}
      </div>
    </div>
  );
}

const tipoHuellaLabel: Record<string, string> = {
  frenada: "Frenada",
  derrape: "Derrape (yaw)",
  arrastre: "Arrastre",
  aceleracion: "Aceleración",
};

const tipoDanoLabel: Record<string, string> = {
  vehiculo_aparcado: "Vehículo aparcado",
  valla: "Valla",
  arbol: "Árbol",
  bordillo: "Bordillo",
  señal: "Señal",
  muro: "Muro",
  otro: "Otro",
};

export function EscenaPanel({ escena }: Props) {
  if (!escena) {
    return (
      <div className="p-6 text-center text-veridict-gray text-sm">
        Sin datos de escena registrados por el perito.
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      {/* Datos generales del perito */}
      <section className="p-4 rounded-lg bg-veridict-green-800 border border-veridict-green-600">
        <div className="flex items-center gap-2 mb-3 text-veridict-lime">
          <Eye className="w-4 h-4" />
          <h4 className="text-sm font-medium">Datos del perito</h4>
        </div>
        <div className="grid md:grid-cols-3 gap-3">
          <Field
            label="Punto impacto"
            value={
              escena.punto_impacto_lat != null && escena.punto_impacto_lon != null
                ? `${escena.punto_impacto_lat.toFixed(5)}, ${escena.punto_impacto_lon.toFixed(5)}`
                : null
            }
          />
          <Field
            label="Ángulo de impacto"
            value={escena.angulo_impacto_deg != null ? `${escena.angulo_impacto_deg}°` : null}
          />
          <Field
            label="Ancho de carril"
            value={escena.ancho_carril_m != null ? `${escena.ancho_carril_m} m` : null}
          />
          <Field
            label="Visibilidad"
            value={
              escena.distancia_visibilidad_m != null ? `${escena.distancia_visibilidad_m} m` : null
            }
          />
          <Field label="Estado asfalto" value={escena.estado_asfalto} />
          <Field label="Señalización" value={escena.señalizacion_visible} />
          <Field
            label="Heading final A"
            value={escena.orientacion_final_a_deg != null ? `${escena.orientacion_final_a_deg}°` : null}
          />
          <Field
            label="Heading final B"
            value={escena.orientacion_final_b_deg != null ? `${escena.orientacion_final_b_deg}°` : null}
          />
        </div>
        {escena.observaciones_perito && (
          <div className="mt-3 text-sm text-veridict-gray italic">
            &quot;{escena.observaciones_perito}&quot;
          </div>
        )}
      </section>

      {/* Huellas */}
      <section>
        <div className="flex items-center gap-2 mb-3 text-veridict-lime">
          <Footprints className="w-4 h-4" />
          <h4 className="text-sm font-medium">
            Huellas en la calzada ({escena.huellas?.length ?? 0})
          </h4>
        </div>
        {!escena.huellas || escena.huellas.length === 0 ? (
          <p className="text-sm text-veridict-gray">Sin huellas registradas.</p>
        ) : (
          <div className="grid md:grid-cols-2 gap-3">
            {escena.huellas.map((h: HuellaCalzada, idx: number) => (
              <div
                key={idx}
                className="p-3 rounded-lg bg-veridict-green-800 border border-veridict-green-600"
              >
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded ${
                      h.vehiculo_id === "A"
                        ? "bg-blue-500/20 text-blue-400"
                        : h.vehiculo_id === "B"
                        ? "bg-orange-500/20 text-orange-400"
                        : "bg-veridict-gray/20 text-veridict-gray"
                    }`}
                  >
                    {h.vehiculo_id}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-veridict-green-700 text-veridict-white">
                    {tipoHuellaLabel[h.tipo] ?? h.tipo}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-veridict-green-700 text-veridict-gray inline-flex items-center gap-1">
                    <Compass className="w-3 h-3" /> {h.curvatura}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <Field label="Longitud" value={`${h.longitud_m} m`} />
                  <Field label="Ancho" value={h.ancho_cm != null ? `${h.ancho_cm} cm` : null} />
                  <Field label="Inicio (x,y)" value={`(${h.inicio[0]}, ${h.inicio[1]})`} />
                  <Field label="Fin (x,y)" value={`(${h.fin[0]}, ${h.fin[1]})`} />
                </div>
                {h.observaciones && (
                  <p className="text-xs text-veridict-gray mt-2 italic">{h.observaciones}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Daños secundarios */}
      <section>
        <div className="flex items-center gap-2 mb-3 text-veridict-lime">
          <AlertOctagon className="w-4 h-4" />
          <h4 className="text-sm font-medium">
            Daños secundarios ({escena.daños_secundarios?.length ?? 0})
          </h4>
        </div>
        {!escena.daños_secundarios || escena.daños_secundarios.length === 0 ? (
          <p className="text-sm text-veridict-gray">Sin daños secundarios registrados.</p>
        ) : (
          <div className="grid md:grid-cols-2 gap-3">
            {escena.daños_secundarios.map((d: DanoSecundario, idx: number) => (
              <div
                key={idx}
                className="p-3 rounded-lg bg-veridict-green-800 border border-veridict-green-600"
              >
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <span className="text-xs px-2 py-0.5 rounded bg-veridict-error/20 text-veridict-error">
                    {tipoDanoLabel[d.tipo] ?? d.tipo}
                  </span>
                  <span className="text-xs text-veridict-gray">{d.lado_calzada}</span>
                  {d.vehiculo_causante && (
                    <span className="text-xs px-2 py-0.5 rounded bg-veridict-green-700 text-veridict-white">
                      Causante: {d.vehiculo_causante}
                    </span>
                  )}
                </div>
                <p className="text-sm text-veridict-white">{d.descripcion}</p>
                <p className="text-xs text-veridict-gray font-mono mt-1">
                  Posición: ({d.posicion[0]}, {d.posicion[1]})
                </p>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
