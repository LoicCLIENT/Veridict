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
        No context data available.
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
            <h4 className="text-sm font-medium">Location</h4>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Address" value={direccion} />
            <Field label="City" value={municipio} />
            <Field label="State/Province" value={provincia} />
          </div>
        </section>

        {/* Vía */}
        <section className="p-4 rounded-lg bg-veridict-green-800 border border-veridict-green-600">
          <div className="flex items-center gap-2 mb-3 text-veridict-lime">
            <Navigation className="w-4 h-4" />
            <h4 className="text-sm font-medium">Road</h4>
          </div>
          {via ? (
            <div className="grid grid-cols-2 gap-3">
              <Field label="Type" value={via.tipo_via} />
              <Field label="Name" value={via.nombre_via} />
              <Field
                label="Speed limit"
                value={via.velocidad_maxima != null ? `${via.velocidad_maxima} km/h` : null}
              />
              <Field label="Lanes" value={via.num_carriles} />
              <Field label="Surface" value={via.superficie} />
              <Field label="Lighting" value={via.iluminacion} />
              <Field label="Source" value={via.fuente} />
            </div>
          ) : (
            <p className="text-sm text-veridict-gray">No data.</p>
          )}
        </section>

        {/* Meteorología */}
        <section className="p-4 rounded-lg bg-veridict-green-800 border border-veridict-green-600">
          <div className="flex items-center gap-2 mb-3 text-veridict-lime">
            <Cloud className="w-4 h-4" />
            <h4 className="text-sm font-medium">Weather</h4>
          </div>
          {meteo ? (
            <div className="grid grid-cols-2 gap-3">
              <Field
                label="Temperature"
                value={meteo.temperatura != null ? `${meteo.temperatura} °C` : null}
              />
              <Field label="Humidity" value={meteo.humedad != null ? `${meteo.humedad}%` : null} />
              <Field
                label="Precipitation"
                value={meteo.precipitacion != null ? `${meteo.precipitacion} mm/h` : null}
              />
              <Field
                label="Wind"
                value={
                  meteo.viento_velocidad != null
                    ? `${meteo.viento_velocidad} km/h ${meteo.viento_direccion ?? ""}`
                    : null
                }
              />
              <Field label="Visibility" value={meteo.visibilidad} />
              <Field label="Cloud cover" value={meteo.nubosidad} />
              <Field label="Conditions" value={meteo.estado_tiempo} />
              <Field label="Source" value={meteo.fuente} />
            </div>
          ) : (
            <p className="text-sm text-veridict-gray">No data.</p>
          )}
        </section>

        {/* Sol */}
        <section className="p-4 rounded-lg bg-veridict-green-800 border border-veridict-green-600">
          <div className="flex items-center gap-2 mb-3 text-veridict-lime">
            <Sun className="w-4 h-4" />
            <h4 className="text-sm font-medium">Sun Position</h4>
          </div>
          {sol ? (
            <div className="grid grid-cols-2 gap-3">
              <Field label="Azimuth" value={sol.azimuth != null ? `${sol.azimuth.toFixed(1)}°` : null} />
              <Field
                label="Altitude"
                value={sol.altitude != null ? `${sol.altitude.toFixed(1)}°` : null}
              />
              <Field label="Daytime?" value={sol.es_dia == null ? null : sol.es_dia ? "Yes" : "No"} />
              <Field
                label="Glare"
                value={
                  sol.deslumbramiento_posible == null
                    ? null
                    : sol.deslumbramiento_posible
                    ? "Possible"
                    : "No"
                }
              />
              <Field label="Sunrise" value={sol.hora_amanecer} />
              <Field label="Sunset" value={sol.hora_atardecer} />
            </div>
          ) : (
            <p className="text-sm text-veridict-gray">No data.</p>
          )}
        </section>
      </div>
    </div>
  );
}
