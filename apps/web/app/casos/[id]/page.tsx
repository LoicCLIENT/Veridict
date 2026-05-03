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
import { InformeDocumento } from "@/components/InformeDocumento";
import { ChatInfoFaltante } from "@/components/ChatInfoFaltante";
import { RazonamientoOrquestadorView } from "@/components/RazonamientoOrquestador";
import { SpecialistTrace } from "@/components/SpecialistTrace";
import type { InformePericial } from "@veridict/types";
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
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  Shield,
  Cloud,
  Car,
  Eye,
  FileText,
  FileSignature,
  Sparkles,
  RefreshCw,
  Loader2,
  Brain,
  ClipboardList,
  X,
  Copy,
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
  const [informe, setInforme] = useState<InformePericial | null>(null);
  const [informeLoading, setInformeLoading] = useState(true);
  const [informeRegenerating, setInformeRegenerating] = useState(false);
  const [showFormulario, setShowFormulario] = useState(false);

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

  // Cargar informe v2 + polling
  useEffect(() => {
    let cancelled = false;
    const fetchInforme = async () => {
      try {
        const data = await api.getInforme(casoId);
        if (!cancelled) setInforme(data);
      } catch {
        if (!cancelled) setInforme(null);
      } finally {
        if (!cancelled) setInformeLoading(false);
      }
    };
    fetchInforme();
    const id = setInterval(fetchInforme, 3000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [casoId]);

  const handleRegenerarInforme = async () => {
    setInformeRegenerating(true);
    try {
      const data = await api.generarInforme(casoId);
      setInforme(data);
      toast.success("Informe regenerado", "Veridict ha actualizado el borrador.");
    } catch (e) {
      console.error(e);
      toast.error("Error", "No se pudo regenerar el informe.");
    } finally {
      setInformeRegenerating(false);
    }
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
    { id: "informe", label: "Informe", icon: FileSignature },
    { id: "razonamiento", label: "Razonamiento", icon: Brain },
    { id: "mapa", label: "Simulación", icon: Map },
    { id: "cronologia", label: "Cronología", icon: Clock },
    { id: "calculos", label: "Cálculos", icon: Calculator },
    { id: "confrontacion", label: "Confrontación", icon: Shield },
    { id: "legal", label: "Marco legal", icon: Scale },
    { id: "contexto", label: "Contexto", icon: Cloud },
    { id: "vehiculos", label: "Vehículos", icon: Car },
    { id: "escena", label: "Escena", icon: Eye },
    { id: "docs", label: "Docs/Fotos", icon: FileText },
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
          {caso.formulario_origen && (
            <Button variant="outline" onClick={() => setShowFormulario(true)}>
              <ClipboardList className="w-4 h-4 mr-2" />
              Ver formulario
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
                  {panelActivo === "informe" && (
                    <div className="p-4 md:p-6">
                      {informeLoading ? (
                        <div className="flex items-center gap-3 text-zinc-400 p-6">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Cargando informe…
                        </div>
                      ) : !informe ? (
                        <div className="flex flex-col items-center justify-center py-16 text-center gap-4">
                          <FileSignature className="w-12 h-12 text-zinc-600" />
                          <div>
                            <p className="text-white font-medium">El informe aún no se ha generado.</p>
                            <p className="text-xs text-zinc-500 mt-1">
                              Pulsa para que Veridict redacte el borrador con los datos del caso.
                            </p>
                          </div>
                          <Button
                            onClick={handleRegenerarInforme}
                            disabled={informeRegenerating}
                            className="bg-blue-600 hover:bg-blue-500"
                          >
                            {informeRegenerating ? (
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                              <Sparkles className="w-4 h-4 mr-2" />
                            )}
                            Generar informe
                          </Button>
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                          {/* Documento del informe */}
                          <div className="lg:col-span-2 space-y-6">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => setPanelActivo("razonamiento")}
                                  className="border-blue-500/40 text-blue-300 hover:bg-blue-500/10"
                                >
                                  <Brain className="w-3.5 h-3.5 mr-2" />
                                  Ver razonamiento del orquestador
                                </Button>
                              </div>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={handleRegenerarInforme}
                                disabled={informeRegenerating}
                                className="border-zinc-700 text-zinc-300"
                              >
                                {informeRegenerating ? (
                                  <Loader2 className="w-3.5 h-3.5 mr-2 animate-spin" />
                                ) : (
                                  <RefreshCw className="w-3.5 h-3.5 mr-2" />
                                )}
                                Regenerar
                              </Button>
                            </div>

                            {/* Sección de razonamiento condensada arriba del documento */}
                            <RazonamientoOrquestadorView
                              casoId={casoId}
                              onNavigateToPanel={(panel) => setPanelActivo(panel)}
                            />

                            <InformeDocumento informe={informe} caso={caso} onInformeUpdate={setInforme} />
                          </div>
                          {/* Chat lateral */}
                          <div className="lg:col-span-1">
                            <div className="sticky top-4">
                              <ChatInfoFaltante
                                casoId={casoId}
                                informe={informe}
                                onUpdate={setInforme}
                              />
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                  {panelActivo === "razonamiento" && (
                    <div className="p-4 md:p-6">
                      <RazonamientoOrquestadorView
                        casoId={casoId}
                        onNavigateToPanel={(panel) => setPanelActivo(panel)}
                      />
                    </div>
                  )}
                  {panelActivo === "mapa" && (
                    <div className="p-4 md:p-6 space-y-4">
                      <SpecialistTrace
                        casoId={casoId}
                        tools={["obtener_frame_simulacion", "simular_fisica"]}
                        title="Trabajo del SimulacionAgent"
                        description="Frames de la simulación física que el orquestador ha pedido para reconstruir la dinámica del siniestro."
                      />
                      <MapaReconstruccion ubicacion={caso.ubicacion} />
                    </div>
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
                    <div className="p-4 md:p-6 space-y-4">
                      <SpecialistTrace
                        casoId={casoId}
                        tools={["simular_fisica", "analizar_biomecanica"]}
                        title="Trabajo del SimulacionAgent y BiomecanicaAgent"
                        description="Cálculos físicos deterministas (CRASH3, balance momento, Stannard-Baker, WAD) y patrón biomecánico que el orquestador ha citado para inferir velocidades y compatibilidad lesional."
                      />
                      <CalculosFisicos calculos={caso.resultado?.calculos || []} />
                    </div>
                  )}
                  {panelActivo === "legal" && (
                    <div className="p-4 md:p-6 space-y-4">
                      <SpecialistTrace
                        casoId={casoId}
                        tools={["consultar_legal"]}
                        title="Trabajo del LegalAgent"
                        description="Artículos del RGC/LSV/RGV consultados en el BOE y jurisprudencia citada por el specialist legal."
                      />
                      <RazonamientoLegal
                        infracciones={caso.resultado?.infracciones || []}
                        veredicto={caso.resultado?.veredicto}
                      />
                    </div>
                  )}
                  {panelActivo === "confrontacion" && (
                    <div className="p-4 md:p-6 space-y-4">
                      <SpecialistTrace
                        casoId={casoId}
                        tools={["verificar_atestado", "analizar_conformidad_atestado"]}
                        title="Trabajo del AtestadoAgent y ConformidadAgent"
                        description="Verificación de incongruencias entre las versiones del atestado y la evidencia física, y análisis de conformidad procesal."
                      />
                      <ConfrontacionTab
                        vehiculos={caso.vehiculos ?? []}
                        contrastes={caso.resultado?.contraste_versiones}
                        compatibilidad={caso.resultado?.compatibilidad_versiones}
                        calculos={caso.resultado?.calculos}
                        adversarial={caso.resultado?.verificacion_adversarial}
                      />
                    </div>
                  )}
                  {panelActivo === "contexto" && (
                    <div className="p-4 md:p-6 space-y-4">
                      <SpecialistTrace
                        casoId={casoId}
                        tools={["consultar_meteo"]}
                        title="Trabajo del MeteoAgent"
                        description="Datos meteorológicos históricos (Open-Meteo) y posición solar (deslumbramiento) en el momento del siniestro."
                      />
                      <ContextoPanel contexto={caso.resultado?.contexto ?? caso.contexto} />
                    </div>
                  )}
                  {panelActivo === "vehiculos" && (
                    <div className="p-4 md:p-6 space-y-4">
                      <SpecialistTrace
                        casoId={casoId}
                        tools={["consultar_ficha_tecnica"]}
                        title="Trabajo del FichaAgent"
                        description="Ficha técnica completa de cada vehículo (masa, dimensiones, rigidez, sistemas de seguridad) consultada por el specialist."
                      />
                      <VehiculosPanel vehiculos={caso.vehiculos ?? []} />
                    </div>
                  )}
                  {panelActivo === "escena" && (
                    <div className="p-4 md:p-6 space-y-4">
                      <SpecialistTrace
                        casoId={casoId}
                        tools={["consultar_escena"]}
                        title="Trabajo del EscenaAgent"
                        description="Geometría de la vía (OSM Overpass), señalización, pendiente (DEM), e imágenes ground-level (Mapillary) recopiladas por el specialist."
                      />
                      <EscenaPanel escena={caso.escena} />
                    </div>
                  )}
                  {panelActivo === "docs" && (
                    <div className="p-4 md:p-6 space-y-4">
                      <SpecialistTrace
                        casoId={casoId}
                        tools={[
                          "listar_biblioteca_fotos",
                          "buscar_foto_perito",
                          "analizar_imagen_dano",
                        ]}
                        title="Trabajo de BibliotecaFotos y Vision"
                        description="Indexado por visión Claude de la biblioteca fotográfica del caso y análisis de daños sobre fotografías concretas pedidas por el orquestador."
                      />
                      <DocumentosPanel
                        documentos={caso.documentos ?? []}
                        fotos={caso.fotos ?? []}
                      />
                    </div>
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

      {/* ── Modal: Ver formulario original ─────────────────────────────── */}
      {showFormulario && caso.formulario_origen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
          onClick={() => setShowFormulario(false)}
        >
          <div
            className="bg-zinc-950 border border-zinc-700 rounded-xl shadow-2xl w-full max-w-3xl max-h-[85vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800">
              <div className="flex items-center gap-2">
                <ClipboardList className="w-5 h-5 text-blue-400" />
                <h3 className="text-white font-medium">Formulario original del caso</h3>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    const blob = new Blob(
                      [JSON.stringify(caso.formulario_origen, null, 2)],
                      { type: "application/json" },
                    );
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `caso_${caso.id.slice(0, 8)}_formulario.json`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Descargar JSON
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    navigator.clipboard.writeText(
                      JSON.stringify(caso.formulario_origen, null, 2),
                    );
                    toast.success("Copiado", "JSON del formulario en el portapapeles.");
                  }}
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Copiar
                </Button>
                <button
                  onClick={() => setShowFormulario(false)}
                  className="p-1 text-zinc-400 hover:text-white"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            <pre className="flex-1 overflow-auto p-5 text-xs text-zinc-200 font-mono whitespace-pre-wrap break-words">
              {JSON.stringify(caso.formulario_origen, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
