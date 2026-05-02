"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { InformePericial, RespuestaPregunta, FichaTecnicaVehiculo, FuenteNormativa } from "@veridict/types";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChatInfoFaltante } from "./ChatInfoFaltante";
import { Loader2, Sparkles, BookOpen, Car, Calculator, FileSignature, RefreshCw } from "lucide-react";

interface Props {
  casoId: string;
}

export function InformePericialView({ casoId }: Props) {
  const [informe, setInforme] = useState<InformePericial | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>("");

  const fetchInforme = async () => {
    try {
      const data = await api.getInforme(casoId);
      setInforme(data);
      if (!activeTab && data.respuestas.length > 0) {
        setActiveTab(data.respuestas[0].pregunta_id);
      }
      setError(null);
    } catch {
      setError("aún no generado");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInforme();
    const id = setInterval(fetchInforme, 3000);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [casoId]);

  const regenerar = async () => {
    setRegenerating(true);
    try {
      const data = await api.generarInforme(casoId);
      setInforme(data);
    } finally {
      setRegenerating(false);
    }
  };

  if (loading) {
    return (
      <Card className="bg-zinc-900/50 border-zinc-800">
        <CardContent className="flex items-center gap-3 p-6 text-zinc-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          Cargando informe…
        </CardContent>
      </Card>
    );
  }

  if (error || !informe) {
    return (
      <Card className="bg-zinc-900/50 border-zinc-800">
        <CardContent className="p-6 flex items-center justify-between">
          <div>
            <p className="text-white font-medium">El informe aún no se ha generado.</p>
            <p className="text-xs text-zinc-500 mt-1">
              Pulsa el botón para que Veridict genere el borrador del peritaje.
            </p>
          </div>
          <Button onClick={regenerar} disabled={regenerating} className="bg-blue-600 hover:bg-blue-500">
            {regenerating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
            Generar informe
          </Button>
        </CardContent>
      </Card>
    );
  }

  const activeRespuesta = informe.respuestas.find((r) => r.pregunta_id === activeTab) ?? informe.respuestas[0];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Columna principal — informe */}
      <div className="lg:col-span-2 space-y-6">
        {/* Resumen + confianza */}
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <div>
                <CardTitle className="text-xl text-white flex items-center gap-2">
                  <FileSignature className="w-5 h-5 text-blue-400" />
                  Borrador de informe pericial
                </CardTitle>
                <CardDescription className="mt-1">{informe.resumen_caso}</CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <ConfianzaBadge value={informe.confianza_global} />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={regenerar}
                  disabled={regenerating}
                  className="border-zinc-700 text-zinc-300"
                >
                  {regenerating ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                </Button>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Respuestas C1/C2/C3 con tabs */}
        {informe.respuestas.length > 0 && (
          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader>
              <CardTitle className="text-lg text-white">Respuesta a las preguntas del encargo</CardTitle>
              <CardDescription>El informe responde literalmente a cada cuestión planteada por el solicitante.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2 mb-4 border-b border-zinc-800 pb-3">
                {informe.respuestas.map((r) => (
                  <button
                    key={r.pregunta_id}
                    onClick={() => setActiveTab(r.pregunta_id)}
                    className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                      activeTab === r.pregunta_id || (!activeTab && r === informe.respuestas[0])
                        ? "bg-blue-500/20 text-blue-300 border border-blue-500/40"
                        : "text-zinc-400 hover:text-white border border-transparent"
                    }`}
                  >
                    {r.pregunta_id}
                  </button>
                ))}
              </div>
              {activeRespuesta && <RespuestaCard respuesta={activeRespuesta} />}
            </CardContent>
          </Card>
        )}

        {/* Fichas técnicas enriquecidas */}
        {informe.fichas_tecnicas.length > 0 && (
          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader>
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Car className="w-4 h-4 text-green-400" />
                Fichas técnicas
              </CardTitle>
              <CardDescription>Datos del fabricante cargados automáticamente por Veridict.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {informe.fichas_tecnicas.map((f) => (
                <FichaTecnicaCard key={f.vehiculo_id} ficha={f} />
              ))}
            </CardContent>
          </Card>
        )}

        {/* Cálculos físicos */}
        {informe.calculos.length > 0 && (
          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader>
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Calculator className="w-4 h-4 text-amber-400" />
                Cálculos físicos
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {informe.calculos.map((c, i) => (
                <div key={i} className="p-3 rounded-lg border border-zinc-800 bg-zinc-900/40">
                  <div className="flex items-baseline justify-between">
                    <span className="text-sm font-medium text-white">{c.nombre}</span>
                    <span className="text-base font-bold text-amber-300">
                      {c.valor} <span className="text-xs text-zinc-400">{c.unidad}</span>
                    </span>
                  </div>
                  <p className="text-xs text-zinc-500 mt-1 font-mono">{c.formula}</p>
                  <p className="text-xs text-zinc-400 mt-1">{c.justificacion}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Normativa + bibliografía */}
        {(informe.normativa_aplicable.length > 0 || informe.bibliografia.length > 0) && (
          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader>
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-purple-400" />
                Normativa y bibliografía
              </CardTitle>
              <CardDescription>Marco aplicable según el tipo de encargo.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {informe.normativa_aplicable.map((n, i) => (
                <NormativaCard key={i} fuente={n} />
              ))}
              {informe.bibliografia.length > 0 && (
                <div className="pt-3 mt-3 border-t border-zinc-800">
                  <p className="text-xs uppercase tracking-wide text-zinc-500 mb-2">Bibliografía técnica</p>
                  <ul className="text-sm text-zinc-400 space-y-1 list-disc pl-5">
                    {informe.bibliografia.map((b, i) => (
                      <li key={i}>{b}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Columna lateral — chat info faltante */}
      <div className="lg:col-span-1">
        <div className="sticky top-4">
          <ChatInfoFaltante
            casoId={casoId}
            informe={informe}
            onUpdate={(nuevo) => setInforme(nuevo)}
          />
        </div>
      </div>
    </div>
  );
}

function ConfianzaBadge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = pct >= 75 ? "bg-green-500/20 text-green-300 border-green-500/40"
    : pct >= 50 ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
    : "bg-red-500/20 text-red-300 border-red-500/40";
  return <Badge className={`${color} border`}>Confianza {pct}%</Badge>;
}

function RespuestaCard({ respuesta }: { respuesta: RespuestaPregunta }) {
  return (
    <div>
      <div className="flex items-start gap-2 mb-3">
        <span className="text-xs font-mono text-blue-400 mt-1">{respuesta.pregunta_id}</span>
        <p className="text-sm text-zinc-300 italic">{respuesta.pregunta}</p>
      </div>
      <p className="text-sm text-zinc-100 leading-relaxed whitespace-pre-line">{respuesta.respuesta}</p>
      {respuesta.citas.length > 0 && (
        <div className="mt-4 pt-3 border-t border-zinc-800">
          <p className="text-xs uppercase tracking-wide text-zinc-500 mb-2">Citas</p>
          <div className="flex flex-wrap gap-1.5">
            {respuesta.citas.map((c, i) => (
              <span
                key={i}
                title={c.extracto ?? undefined}
                className="text-xs px-2 py-1 rounded bg-zinc-800 text-zinc-300 border border-zinc-700"
              >
                <span className="text-zinc-500 mr-1">{c.tipo}:</span>
                {c.referencia}
              </span>
            ))}
          </div>
        </div>
      )}
      <div className="mt-3 text-xs text-zinc-500">Confianza de esta respuesta: {Math.round(respuesta.confianza * 100)}%</div>
    </div>
  );
}

function FichaTecnicaCard({ ficha }: { ficha: FichaTecnicaVehiculo }) {
  return (
    <div className="p-3 rounded-lg border border-zinc-800 bg-zinc-900/40">
      <div className="flex items-baseline justify-between mb-1">
        <span className="text-sm font-medium text-white">
          {ficha.vehiculo_id} — {ficha.marca} {ficha.modelo}
          {ficha.anio ? ` (${ficha.anio})` : ""}
        </span>
        {ficha.fuente && <span className="text-xs text-zinc-500">{ficha.fuente}</span>}
      </div>
      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-zinc-400">
        {ficha.masa_kg != null && <span>Masa: <span className="text-zinc-200">{ficha.masa_kg} kg</span></span>}
        {ficha.longitud_m != null && <span>Longitud: <span className="text-zinc-200">{ficha.longitud_m} m</span></span>}
        {ficha.altura_parachoques_m && (
          <span>Altura parachoques: <span className="text-zinc-200">{ficha.altura_parachoques_m[0]}–{ficha.altura_parachoques_m[1]} m</span></span>
        )}
        {ficha.altura_largueros_m != null && (
          <span>Largueros: <span className="text-zinc-200">{ficha.altura_largueros_m} m</span></span>
        )}
      </div>
      {ficha.sistemas_seguridad.length > 0 && (
        <div className="mt-2">
          <p className="text-xs text-zinc-500 mb-1">Sistemas de seguridad</p>
          <ul className="text-xs text-zinc-300 space-y-0.5 list-disc pl-4">
            {ficha.sistemas_seguridad.map((s, i) => <li key={i}>{s}</li>)}
          </ul>
        </div>
      )}
      {ficha.notas && <p className="text-xs text-zinc-500 italic mt-2">{ficha.notas}</p>}
    </div>
  );
}

function NormativaCard({ fuente }: { fuente: FuenteNormativa }) {
  return (
    <div className="p-2.5 rounded-lg border border-zinc-800 bg-zinc-900/40">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-sm font-medium text-purple-300">{fuente.referencia}</span>
        {fuente.boe && <span className="text-xs text-zinc-500">{fuente.boe}</span>}
      </div>
      <p className="text-xs text-zinc-300 mt-1">{fuente.titulo}</p>
      {fuente.extracto && (
        <p className="text-xs text-zinc-500 italic mt-1 border-l-2 border-zinc-700 pl-2">«{fuente.extracto}»</p>
      )}
    </div>
  );
}
