"use client";

export const dynamic = "force-dynamic";
export const dynamicParams = true;

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { api, type Caso } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { MapaReconstruccion } from "@/components/MapaReconstruccion";
import { CalculosFisicos } from "@/components/CalculosFisicos";
import { RazonamientoLegal } from "@/components/RazonamientoLegal";
import { Timeline, ConfrontacionTab } from "@/components/caso";
import { ContextoPanel } from "@/components/caso/ContextoPanel";
import { VehiculosPanel } from "@/components/caso/VehiculosPanel";
import { EscenaPanel } from "@/components/caso/EscenaPanel";
import { DocumentosPanel } from "@/components/caso/DocumentosPanel";
import { mapEventosToTimeline } from "@/lib/mapTimeline";
import { useToast } from "@/components/ui/toast";
import {
  ProcessingPipeline,
  type AgentState,
} from "@/components/processing";
import { mapEstadoToAgents, isTerminal } from "@/lib/mapEstado";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Map,
  Clock,
  Calculator,
  Scale,
  Download,
  Play,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  Shield,
  Cloud,
  Car,
  Eye,
  FileText,
} from "lucide-react";
import Link from "next/link";

export default function CasoDetailPage() {
  const params = useParams();
  const casoId = params.id as string;
  const toast = useToast();
  const [caso, setCaso] = useState<Caso | null>(null);
  const [loading, setLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [agentStates, setAgentStates] = useState<AgentState[]>([
    { agent: "extractor", status: "idle" },
    { agent: "reconstructor", status: "idle" },
    { agent: "legal", status: "idle" },
    { agent: "adversarial", status: "idle" },
  ]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const { panelActivo, setPanelActivo } = useAppStore();

  useEffect(() => {
    async function loadCaso() {
      try {
        const data = await api.getCaso(casoId);
        setCaso(data);
      } catch (error) {
        console.error("Error loading caso:", error);
        toast.error(
          "Error de red",
          "No se pudo cargar el caso. Verifica que el backend esté disponible."
        );
        setCaso(null);
      } finally {
        setLoading(false);
      }
    }
    loadCaso();
  }, [casoId, toast]);

  const handleAnalizar = async () => {
    if (!caso) return;
    try {
      await api.iniciarAnalisis(caso.id);
    } catch (error) {
      console.error("Error iniciando análisis:", error);
      toast.error("Error", "No se pudo iniciar el análisis.");
      return;
    }
    setIsProcessing(true);
    setOverallProgress(0);
    setCaso({ ...caso, estado: "procesando" });

    const intervalId = setInterval(async () => {
      try {
        const estado = await api.getEstado(caso.id);
        setAgentStates(mapEstadoToAgents(estado));
        setOverallProgress(estado.progreso ?? 0);

        const terminal = isTerminal(estado);
        if (terminal === "completado") {
          clearInterval(intervalId);
          try {
            const resultado = await api.getDictamen(caso.id);
            setCaso((prev) =>
              prev ? { ...prev, estado: "completado", resultado } : prev
            );
            toast.success(
              "Análisis completado",
              "Los 4 agentes han procesado el caso exitosamente."
            );
          } catch (e) {
            console.error("Error fetching dictamen:", e);
            toast.error("Error", "No se pudo obtener el dictamen final.");
          }
          setIsProcessing(false);
        } else if (terminal === "error") {
          clearInterval(intervalId);
          setIsProcessing(false);
          setCaso((prev) =>
            prev ? { ...prev, estado: "escalado_humano" } : prev
          );
          toast.error(
            "Análisis fallido",
            estado.etapa_actual || "El análisis no pudo completarse."
          );
        }
      } catch (e) {
        console.error("Error polling estado:", e);
        clearInterval(intervalId);
        setIsProcessing(false);
        toast.error("Error de red", "Se perdió la conexión con el backend.");
      }
    }, 1500);
  };

  const handleDownloadPdf = async () => {
    if (!caso) return;
    try {
      const blob = await api.downloadPdf(caso.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `dictamen_${caso.id}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(
        "PDF descargado",
        `Dictamen UNE-EN 16775 del caso #${caso.id}`
      );
    } catch (error) {
      console.error("Error downloading PDF:", error);
      toast.error(
        "Error al descargar",
        "No se pudo generar el PDF. Intenta de nuevo."
      );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-veridict-lime border-t-transparent rounded-full animate-spin" />
          <span className="text-veridict-gray">Cargando caso...</span>
        </div>
      </div>
    );
  }

  if (!caso) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="p-8 text-center">
          <AlertTriangle className="w-12 h-12 text-veridict-error mx-auto mb-4" />
          <h2 className="text-xl font-medium mb-2">Caso no encontrado</h2>
          <p className="text-veridict-gray mb-4">
            El caso #{casoId} no existe o ha sido eliminado.
          </p>
          <Link href="/casos">
            <Button variant="outline">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Volver a casos
            </Button>
          </Link>
        </Card>
      </div>
    );
  }

  const tabs = [
    { id: "mapa", label: "Mapa", icon: Map },
    { id: "cronologia", label: "Cronología", icon: Clock },
    { id: "calculos", label: "Cálculos", icon: Calculator },
    { id: "legal", label: "Legal", icon: Scale },
    { id: "confrontacion", label: "Confrontación", icon: Shield },
    { id: "contexto", label: "Contexto", icon: Cloud },
    { id: "vehiculos", label: "Vehículos", icon: Car },
    { id: "escena", label: "Escena", icon: Eye },
    { id: "docs", label: "Docs/Fotos", icon: FileText },
    { id: "dictamen", label: "Dictamen", icon: Scale },
  ] as const;

  const estadoBadge = {
    creado: { label: "Pendiente", variant: "outline" as const },
    procesando: { label: "Procesando", variant: "default" as const },
    completado: { label: "Completado", variant: "default" as const },
    escalado_humano: { label: "Revisión", variant: "destructive" as const },
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <motion.div
        className="flex justify-between items-start mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="flex items-start gap-4">
          <Link href="/casos">
            <Button variant="ghost" size="icon" className="mt-1">
              <ArrowLeft className="w-5 h-5" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-veridict-white">
                Caso #{caso.id}
              </h1>
              <Badge
                variant={estadoBadge[caso.estado].variant}
                className={
                  caso.estado === "completado"
                    ? "bg-veridict-lime/20 text-veridict-lime border-veridict-lime/40"
                    : caso.estado === "procesando"
                    ? "bg-veridict-lime/10 text-veridict-lime animate-pulse"
                    : ""
                }
              >
                {estadoBadge[caso.estado].label}
              </Badge>
            </div>
            <p className="text-veridict-gray">
              {new Date(caso.fecha_accidente).toLocaleDateString("es-ES", {
                weekday: "long",
                year: "numeric",
                month: "long",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          {caso.estado === "creado" && (
            <Button onClick={handleAnalizar}>
              <Play className="w-4 h-4 mr-2" />
              Analizar con IA
            </Button>
          )}
          {caso.estado === "completado" && (
            <Button onClick={handleDownloadPdf}>
              <Download className="w-4 h-4 mr-2" />
              Descargar PDF
            </Button>
          )}
        </div>
      </motion.div>

      {/* Vista de procesamiento */}
      <AnimatePresence mode="wait">
        {isProcessing ? (
          <motion.div
            key="processing"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
            className="max-w-lg mx-auto py-12"
          >
            <ProcessingPipeline
              agents={agentStates}
              overallProgress={overallProgress}
              variant="vertical"
            />
          </motion.div>
        ) : (
          <motion.div
            key="content"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {/* Tabs */}
            <div className="flex gap-2 mb-6">
              {tabs.map((tab) => (
                <Button
                  key={tab.id}
                  variant={panelActivo === tab.id ? "default" : "outline"}
                  onClick={() => setPanelActivo(tab.id)}
                  className="flex items-center gap-2"
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </Button>
              ))}
            </div>

            {/* Content - Full Width */}
            <Card className="min-h-[600px] overflow-hidden">
              <AnimatePresence mode="wait">
                <motion.div
                  key={panelActivo}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.2 }}
                  className="h-full"
                >
                  {panelActivo === "mapa" && (
                    <MapaReconstruccion ubicacion={caso.ubicacion} />
                  )}
                  {panelActivo === "cronologia" && (
                    <div className="p-4 h-full">
                      <Timeline
                        events={mapEventosToTimeline(caso.resultado?.cronologia ?? [])}
                        currentTime={currentTime}
                        onTimeChange={setCurrentTime}
                      />
                    </div>
                  )}
                  {panelActivo === "calculos" && (
                    <CalculosFisicos calculos={caso.resultado?.calculos || []} />
                  )}
                  {panelActivo === "legal" && (
                    <RazonamientoLegal
                      infracciones={caso.resultado?.infracciones || []}
                      veredicto={caso.resultado?.veredicto}
                    />
                  )}
                  {panelActivo === "confrontacion" && (
                    <ConfrontacionTab
                      vehiculos={caso.vehiculos ?? []}
                      contrastes={caso.resultado?.contraste_versiones}
                      compatibilidad={caso.resultado?.compatibilidad_versiones}
                      calculos={caso.resultado?.calculos}
                      adversarial={caso.resultado?.verificacion_adversarial}
                    />
                  )}
                  {panelActivo === "contexto" && (
                    <ContextoPanel contexto={caso.resultado?.contexto ?? caso.contexto} />
                  )}
                  {panelActivo === "vehiculos" && (
                    <VehiculosPanel vehiculos={caso.vehiculos ?? []} />
                  )}
                  {panelActivo === "escena" && <EscenaPanel escena={caso.escena} />}
                  {panelActivo === "docs" && (
                    <DocumentosPanel
                      documentos={caso.documentos ?? []}
                      fotos={caso.fotos ?? []}
                    />
                  )}
                  {panelActivo === "dictamen" && (
                    <div className="p-6">
                      <h3 className="font-semibold text-veridict-white mb-6 flex items-center gap-2 text-xl">
                        <Scale className="w-6 h-6 text-veridict-lime" />
                        Resumen del Dictamen
                      </h3>

                      {caso.resultado ? (
                        <div className="grid md:grid-cols-2 gap-6">
                          {/* Veredicto */}
                          <div className="md:col-span-2">
                            <h4 className="text-sm font-medium text-veridict-gray mb-3">
                              Atribución de culpa
                            </h4>
                            <div className="flex gap-6">
                              <motion.div
                                className="flex-1 p-6 rounded-lg bg-blue-500/10 border border-blue-500/20"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.1 }}
                              >
                                <div className="text-sm text-blue-400 mb-2">
                                  Vehículo A
                                </div>
                                <div className="text-5xl font-bold text-blue-400">
                                  {Math.round((caso.resultado.veredicto?.culpa_a ?? 0) * 100)}%
                                </div>
                              </motion.div>
                              <motion.div
                                className="flex-1 p-6 rounded-lg bg-orange-500/10 border border-orange-500/20"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.2 }}
                              >
                                <div className="text-sm text-orange-400 mb-2">
                                  Vehículo B
                                </div>
                                <div className="text-5xl font-bold text-orange-400">
                                  {Math.round((caso.resultado.veredicto?.culpa_b ?? 0) * 100)}%
                                </div>
                              </motion.div>
                            </div>
                            <div className="mt-3 text-center">
                              <span className="text-sm text-veridict-gray">
                                Confianza del modelo:{" "}
                                <span className="text-veridict-lime font-mono text-lg">
                                  {Math.round((caso.resultado.veredicto?.confidence ?? 0) * 100)}%
                                </span>
                              </span>
                            </div>
                          </div>

                          {/* Compatibilidad versiones */}
                          <div>
                            <h4 className="text-sm font-medium text-veridict-gray mb-3">
                              Compatibilidad de versiones
                            </h4>
                            <div className="p-4 rounded-lg bg-veridict-green-800 border border-veridict-green-600 h-full">
                              <div className="flex flex-col gap-3 mb-3">
                                <div
                                  className={`flex items-center gap-2 text-sm ${
                                    (caso.resultado.compatibilidad_versiones?.a ?? false)
                                      ? "text-veridict-lime"
                                      : "text-veridict-error"
                                  }`}
                                >
                                  {(caso.resultado.compatibilidad_versiones?.a ?? false) ? (
                                    <CheckCircle2 className="w-5 h-5" />
                                  ) : (
                                    <AlertTriangle className="w-5 h-5" />
                                  )}
                                  <span className="font-medium">Versión A:{" "}</span>
                                  {(caso.resultado.compatibilidad_versiones?.a ?? false)
                                    ? "Compatible con evidencia física"
                                    : "Incompatible con evidencia física"}
                                </div>
                                <div
                                  className={`flex items-center gap-2 text-sm ${
                                    (caso.resultado.compatibilidad_versiones?.b ?? false)
                                      ? "text-veridict-lime"
                                      : "text-veridict-error"
                                  }`}
                                >
                                  {(caso.resultado.compatibilidad_versiones?.b ?? false) ? (
                                    <CheckCircle2 className="w-5 h-5" />
                                  ) : (
                                    <AlertTriangle className="w-5 h-5" />
                                  )}
                                  <span className="font-medium">Versión B:{" "}</span>
                                  {(caso.resultado.compatibilidad_versiones?.b ?? false)
                                    ? "Compatible con evidencia física"
                                    : "Incompatible con evidencia física"}
                                </div>
                              </div>
                              <p className="text-sm text-veridict-gray mt-4 pt-3 border-t border-veridict-green-600">
                                {(caso.resultado.compatibilidad_versiones?.justificacion ?? "")}
                              </p>
                            </div>
                          </div>

                          {/* Devil's Advocate + Audit */}
                          <div className="space-y-4">
                            <div>
                              <h4 className="text-sm font-medium text-veridict-gray mb-3">
                                Verificación adversarial
                              </h4>
                              <div
                                className={`p-4 rounded-lg flex items-center gap-3 ${
                                  (caso.resultado.verificacion_adversarial?.passed ?? false)
                                    ? "bg-veridict-lime/10 border border-veridict-lime/30"
                                    : "bg-veridict-error/10 border border-veridict-error/30"
                                }`}
                              >
                                {(caso.resultado.verificacion_adversarial?.passed ?? false) ? (
                                  <CheckCircle2 className="w-6 h-6 text-veridict-lime" />
                                ) : (
                                  <AlertTriangle className="w-6 h-6 text-veridict-error" />
                                )}
                                <span
                                  className={`font-medium ${
                                    (caso.resultado.verificacion_adversarial?.passed ?? false)
                                      ? "text-veridict-lime"
                                      : "text-veridict-error"
                                  }`}
                                >
                                  {(caso.resultado.verificacion_adversarial?.passed ?? false)
                                    ? "Todas las verificaciones pasadas"
                                    : "Requiere revisión humana"}
                                </span>
                              </div>
                              {!(caso.resultado.verificacion_adversarial?.passed ?? true) &&
                                (caso.resultado.verificacion_adversarial?.failures ?? []).length > 0 && (
                                  <ul className="mt-2 text-xs text-veridict-error/90 list-disc list-inside space-y-1 pl-2">
                                    {caso.resultado.verificacion_adversarial!.failures.map((f, i) => (
                                      <li key={i}>{f}</li>
                                    ))}
                                  </ul>
                                )}
                            </div>

                            {caso.resultado.veredicto?.razonamiento && (
                              <div>
                                <h4 className="text-sm font-medium text-veridict-gray mb-2">
                                  Razonamiento técnico-jurídico
                                </h4>
                                <p className="text-sm text-veridict-white whitespace-pre-wrap leading-relaxed bg-veridict-green-800 border border-veridict-green-600 rounded p-3">
                                  {caso.resultado.veredicto.razonamiento}
                                </p>
                              </div>
                            )}

                            {caso.resultado.veredicto?.advertencia_personal && (
                              <div className="flex items-start gap-2 p-3 rounded bg-yellow-500/10 border border-yellow-500/30">
                                <AlertTriangle className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                                <div className="text-xs text-yellow-300">
                                  <strong>Regla 100/100 TS:</strong> daños personales — la culpa
                                  civil puede no redistribuirse. Revisión humana recomendada.
                                </div>
                              </div>
                            )}

                            <div>
                              <h4 className="text-sm font-medium text-veridict-gray mb-2">
                                Audit trail (Sigstore)
                              </h4>
                              <code className="text-xs text-veridict-gray bg-veridict-green-800 px-3 py-3 rounded block break-all font-mono border border-veridict-green-600">
                                {caso.resultado.sigstore_hash ?? "—"}
                              </code>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="flex flex-col items-center justify-center h-64 text-center">
                          <Play className="w-16 h-16 text-veridict-gray/40 mb-4" />
                          <p className="text-veridict-gray text-lg">
                            Ejecuta el análisis con IA para ver el dictamen
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </motion.div>
              </AnimatePresence>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
