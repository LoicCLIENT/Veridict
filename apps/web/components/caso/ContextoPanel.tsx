"use client";

import type { Contexto } from "@/lib/api";
import { Cloud, MapPin, Sun, Navigation } from "lucide-react";

interface Props {
  contexto?: Contexto | null;
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

export function ContextoPanel({ contexto }: Props) {
  if (!contexto) {
    return (
      <div className="p-6 text-center text-veridict-gray text-sm">
        Sin datos de contexto disponibles.
      </div>
    );
  }

  const { meteo, via, sol, direccion, municipio, provincia } = contexto;

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      <div className="grid md:grid-cols-2 gap-4">
        {/* Ubicación */}
        <section className="p-4 rounded-lg bg-veridict-green-800 border border-veridict-green-600">
          <div className="flex items-center gap-2 mb-3 text-veridict-lime">
            <MapPin className="w-4 h-4" />
            <h4 className="text-sm font-medium">Ubicación</h4>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Dirección" value={direccion} />
            <Field label="Municipio" value={municipio} />
            <Field label="Provincia" value={provincia} />
          </div>
        </section>

        {/* Vía */}
        <section className="p-4 rounded-lg bg-veridict-green-800 border border-veridict-green-600">
          <div className="flex items-center gap-2 mb-3 text-veridict-lime">
            <Navigation className="w-4 h-4" />
            <h4 className="text-sm font-medium">Vía</h4>
          </div>
          {via ? (
            <div className="grid grid-cols-2 gap-3">
              <Field label="Tipo" value={via.tipo_via} />
              <Field label="Nombre" value={via.nombre_via} />
              <Field
                label="Velocidad máx."
                value={via.velocidad_maxima != null ? `${via.velocidad_maxima} km/h` : null}
              />
              <Field label="Carriles" value={via.num_carriles} />
              <Field label="Superficie" value={via.superficie} />
              <Field label="Iluminación" value={via.iluminacion} />
              <Field label="Fuente" value={via.fuente} />
            </div>
          ) : (
            <p className="text-sm text-veridict-gray">Sin datos.</p>
          )}
        </section>

        {/* Meteorología */}
        <section className="p-4 rounded-lg bg-veridict-green-800 border border-veridict-green-600">
          <div className="flex items-center gap-2 mb-3 text-veridict-lime">
            <Cloud className="w-4 h-4" />
            <h4 className="text-sm font-medium">Meteorología</h4>
          </div>
          {meteo ? (
            <div className="grid grid-cols-2 gap-3">
              <Field
                label="Temperatura"
                value={meteo.temperatura != null ? `${meteo.temperatura} °C` : null}
              />
              <Field label="Humedad" value={meteo.humedad != null ? `${meteo.humedad}%` : null} />
              <Field
                label="Precipitación"
                value={meteo.precipitacion != null ? `${meteo.precipitacion} mm/h` : null}
              />
              <Field
                label="Viento"
                value={
                  meteo.viento_velocidad != null
                    ? `${meteo.viento_velocidad} km/h ${meteo.viento_direccion ?? ""}`
                    : null
                }
              />
              <Field label="Visibilidad" value={meteo.visibilidad} />
              <Field label="Nubosidad" value={meteo.nubosidad} />
              <Field label="Estado" value={meteo.estado_tiempo} />
              <Field label="Fuente" value={meteo.fuente} />
            </div>
          ) : (
            <p className="text-sm text-veridict-gray">Sin datos.</p>
          )}
        </section>

        {/* Sol */}
        <section className="p-4 rounded-lg bg-veridict-green-800 border border-veridict-green-600">
          <div className="flex items-center gap-2 mb-3 text-veridict-lime">
            <Sun className="w-4 h-4" />
            <h4 className="text-sm font-medium">Posición solar</h4>
          </div>
          {sol ? (
            <div className="grid grid-cols-2 gap-3">
              <Field label="Azimut" value={sol.azimuth != null ? `${sol.azimuth.toFixed(1)}°` : null} />
              <Field
                label="Altitud"
                value={sol.altitude != null ? `${sol.altitude.toFixed(1)}°` : null}
              />
              <Field label="¿Día?" value={sol.es_dia == null ? null : sol.es_dia ? "Sí" : "No"} />
              <Field
                label="Deslumbramiento"
                value={
                  sol.deslumbramiento_posible == null
                    ? null
                    : sol.deslumbramiento_posible
                    ? "Posible"
                    : "No"
                }
              />
              <Field label="Amanecer" value={sol.hora_amanecer} />
              <Field label="Atardecer" value={sol.hora_atardecer} />
            </div>
          ) : (
            <p className="text-sm text-veridict-gray">Sin datos.</p>
          )}
        </section>
      </div>
    </div>
  );
}
