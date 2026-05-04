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
import { UploadProgressBanner } from "@/components/UploadProgressBanner";
import type { InformePericial } from "@veridict/types";
import { mapEventosToTimeline } from "@/lib/mapTimeline";
import { useToast } from "@/components/ui/toast";
import {
  ProcessingPipeline,
  type AgentState,
} from "@/components/processing";
import { mapEstadoToAgents, isTerminal } from "@/lib/mapEstado";
import { Button } from "@/components/ui/button";
import {
  FileText,
  Play,
  Clock,
  Calculator,
  Scale,
  Download,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  Cloud,
  Car,
  Eye,
  FileImage,
  Sparkles,
  RefreshCw,
  Loader2,
  ChevronRight,
  Crosshair,
  Activity,
  Zap,
  Brain,
  ClipboardList,
  X,
  Copy,
  Map,
} from "lucide-react";
import Link from "next/link";

type TabId = "informe" | "razonamiento" | "simulacion" | "cronologia" | "calculos" | "confrontacion" | "legal" | "contexto" | "vehiculos" | "escena" | "docs";

interface NavItem {
  id: TabId;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  group: "analisis" | "datos" | "evidencia";
}

const navItems: NavItem[] = [
  { id: "informe", label: "Report", icon: FileText, group: "analisis" },
  { id: "razonamiento", label: "Reasoning", icon: Brain, group: "analisis" },
  { id: "simulacion", label: "3D Simulation", icon: Map, group: "analisis" },
  { id: "cronologia", label: "Timeline", icon: Clock, group: "analisis" },
  { id: "calculos", label: "Calculations", icon: Calculator, group: "analisis" },
  { id: "confrontacion", label: "Confrontation", icon: Crosshair, group: "analisis" },
  { id: "legal", label: "Legal Framework", icon: Scale, group: "analisis" },
  { id: "contexto", label: "Context", icon: Cloud, group: "datos" },
  { id: "vehiculos", label: "Vehicles", icon: Car, group: "datos" },
  { id: "escena", label: "Scene", icon: Eye, group: "evidencia" },
  { id: "docs", label: "Documents", icon: FileImage, group: "evidencia" },
];

const groupLabels = {
  analisis: "Analysis",
  datos: "Data",
  evidencia: "Evidence",
};

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
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showFormulario, setShowFormulario] = useState(false);
  const [recentlyEdited, setRecentlyEdited] = useState<string[]>([]);
  const [simulacionLoading, setSimulacionLoading] = useState(false);
  const [simulacionError, setSimulacionError] = useState<string | null>(null);

  const regenerarSimulacion = async () => {
    if (simulacionLoading) return;
    setSimulacionLoading(true);
    setSimulacionError(null);
    try {
      const updated = await api.regenerarSimulacion(casoId);
      setInforme(updated);
      const escena = updated.simulacion_escena;
      if (!escena || !Array.isArray(escena.actores) || escena.actores.length === 0) {
        const falta = (escena?.falta_info && escena.falta_info[0]) || "SimulationAgent did not return valid actors.";
        setSimulacionError(`No reconstructed scene: ${falta}`);
      }
    } catch (e: any) {
      setSimulacionError(e?.message || "Could not regenerate simulation");
    } finally {
      setSimulacionLoading(false);
    }
  };

  const marcarRecentlyEdited = (ids: string[]) => {
    if (ids.length === 0) return;
    setRecentlyEdited(ids);
    setTimeout(() => setRecentlyEdited([]), 6000);
  };

  useEffect(() => {
    async function loadCaso() {
      try {
        const data = await api.getCaso(casoId);
        setCaso(data);
      } catch (error) {
        console.error("Error loading caso:", error);
        toast.error(
          "Network error",
          "Could not load the case. Verify that the backend is available."
        );
        setCaso(null);
      } finally {
        setLoading(false);
      }
    }
    loadCaso();
    // toast intentionally omitted: re-running on toast changes would re-fetch the caso every render
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [casoId]);

  useEffect(() => {
    if (!loading && !caso) return; // skip polling if caso doesn't exist
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
  }, [casoId, loading, caso]);

  const handleRegenerarInforme = async () => {
    setInformeRegenerating(true);
    try {
      const data = await api.generarInforme(casoId);
      setInforme(data);
      toast.success("Report regenerated", "Veridict has updated the draft.");
    } catch (e) {
      console.error(e);
      toast.error("Error", "Could not regenerate the report.");
    } finally {
      setInformeRegenerating(false);
    }
  };

  const handleAnalizar = async () => {
    if (!caso) return;
    try {
      await api.iniciarAnalisis(caso.id);
    } catch (error) {
      console.error("Error starting analysis:", error);
      toast.error("Error", "Could not start the analysis.");
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
              "Analysis completed",
              "All 4 agents have successfully processed the case."
            );
          } catch (e) {
            console.error("Error fetching dictamen:", e);
            toast.error("Error", "Could not retrieve the final verdict.");
          }
          setIsProcessing(false);
        } else if (terminal === "error") {
          clearInterval(intervalId);
          setIsProcessing(false);
          setCaso((prev) =>
            prev ? { ...prev, estado: "escalado_humano" } : prev
          );
          toast.error(
            "Analysis failed",
            estado.etapa_actual || "The analysis could not be completed."
          );
        }
      } catch (e) {
        console.error("Error polling estado:", e);
        clearInterval(intervalId);
        setIsProcessing(false);
        toast.error("Network error", "Connection to the backend was lost.");
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
        "PDF downloaded",
        `UNE-EN 16775 expert report for case #${caso.id}`
      );
    } catch (error) {
      console.error("Error downloading PDF:", error);
      toast.error(
        "Download error",
        "Could not generate the PDF. Please try again."
      );
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="w-12 h-12 border-2 border-[#C2E94B]/20 rounded-full" />
            <div className="absolute inset-0 w-12 h-12 border-2 border-[#C2E94B] border-t-transparent rounded-full animate-spin" />
          </div>
          <span className="text-zinc-500 text-sm">Loading case...</span>
        </div>
      </div>
    );
  }

  // Not found state
  if (!caso) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 rounded-2xl bg-red-500/10 flex items-center justify-center mx-auto mb-6">
            <AlertTriangle className="w-8 h-8 text-red-400" />
          </div>
          <h2 className="text-2xl font-semibold text-white mb-2">Case not found</h2>
          <p className="text-zinc-500 mb-8">
            Case #{casoId} does not exist or has been deleted from the system.
          </p>
          <Link href="/casos">
            <Button className="bg-zinc-800 hover:bg-zinc-700 text-white">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to history
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const estadoConfig = {
    creado: { label: "Pending", color: "bg-zinc-600", textColor: "text-zinc-300" },
    procesando: { label: "Processing", color: "bg-[#C2E94B]", textColor: "text-[#0a0a0a]" },
    completado: { label: "Completed", color: "bg-[#C2E94B]", textColor: "text-[#0a0a0a]" },
    escalado_humano: { label: "Review", color: "bg-amber-500", textColor: "text-amber-950" },
  };

  const currentTab = (panelActivo as TabId) || "informe";

  // Group nav items
  const groupedNav = {
    analisis: navItems.filter(i => i.group === "analisis"),
    datos: navItems.filter(i => i.group === "datos"),
    evidencia: navItems.filter(i => i.group === "evidencia"),
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarCollapsed ? 72 : 260 }}
        transition={{ duration: 0.2, ease: "easeInOut" }}
        className="fixed left-0 top-0 h-screen bg-[#111] border-r border-zinc-800/50 z-40 flex flex-col"
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-zinc-800/50">
          <Link href="/" className="flex items-center gap-3">
            <img
              src="/logo.png"
              alt="Veridict"
              className={sidebarCollapsed ? "h-6 w-auto" : "h-8 w-auto"}
            />
          </Link>
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-1.5 rounded-lg hover:bg-zinc-800 transition-colors"
          >
            <ChevronRight className={`w-4 h-4 text-zinc-500 transition-transform ${sidebarCollapsed ? "" : "rotate-180"}`} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-3">
          {(["analisis", "datos", "evidencia"] as const).map((group) => (
            <div key={group} className="mb-6">
              {!sidebarCollapsed && (
                <p className="text-[10px] font-medium text-zinc-600 uppercase tracking-wider px-3 mb-2">
                  {groupLabels[group]}
                </p>
              )}
              <div className="space-y-1">
                {groupedNav[group].map((item) => {
                  const isActive = currentTab === item.id;
                  const Icon = item.icon;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setPanelActivo(item.id)}
                      className={`
                        w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200
                        ${isActive
                          ? "bg-[#C2E94B]/10 text-[#C2E94B]"
                          : "text-zinc-400 hover:text-white hover:bg-zinc-800/50"
                        }
                        ${sidebarCollapsed ? "justify-center" : ""}
                      `}
                      title={sidebarCollapsed ? item.label : undefined}
                    >
                      <Icon className={`w-[18px] h-[18px] flex-shrink-0 ${isActive ? "text-[#C2E94B]" : ""}`} />
                      {!sidebarCollapsed && (
                        <span className="text-sm font-medium truncate">{item.label}</span>
                      )}
                      {isActive && !sidebarCollapsed && (
                        <div className="ml-auto w-1.5 h-1.5 rounded-full bg-[#C2E94B]" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Bottom actions */}
        <div className="p-3 border-t border-zinc-800/50">
          {caso.estado === "completado" && (
            <button
              onClick={handleDownloadPdf}
              className={`
                w-full flex items-center gap-3 px-3 py-2.5 rounded-xl
                bg-[#C2E94B] text-[#0a0a0a] font-medium text-sm
                hover:bg-[#d4f06d] transition-colors
                ${sidebarCollapsed ? "justify-center" : ""}
              `}
              title={sidebarCollapsed ? "Download PDF" : undefined}
            >
              <Download className="w-[18px] h-[18px]" />
              {!sidebarCollapsed && <span>Download PDF</span>}
            </button>
          )}
        </div>
      </motion.aside>

      {/* Main content */}
      <main
        className="flex-1 transition-all duration-200"
        style={{ marginLeft: sidebarCollapsed ? 72 : 260 }}
      >
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-zinc-800/50">
          <div className="flex items-center justify-between h-16 px-6">
            {/* Left: Back + Case ID */}
            <div className="flex items-center gap-4">
              <Link
                href="/casos"
                className="p-2 rounded-lg hover:bg-zinc-800 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-zinc-400" />
              </Link>
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-lg font-semibold text-white">
                    Case #{caso.id}
                  </h1>
                  <span className={`
                    px-2.5 py-0.5 rounded-full text-xs font-medium
                    ${estadoConfig[caso.estado].color} ${estadoConfig[caso.estado].textColor}
                  `}>
                    {estadoConfig[caso.estado].label}
                  </span>
                </div>
                <p className="text-xs text-zinc-500">
                  {new Date(caso.fecha_accidente).toLocaleDateString("en-US", {
                    weekday: "long",
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </p>
              </div>
            </div>

            {/* Right: Quick stats + Actions */}
            <div className="flex items-center gap-6">
              {/* Quick stats */}
              {caso.estado === "completado" && caso.resultado?.veredicto && (
                <div className="hidden lg:flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                      <Car className="w-4 h-4 text-blue-400" />
                    </div>
                    <div>
                      <p className="text-[10px] text-zinc-500 uppercase">Vehicle A</p>
                      <p className="text-sm font-semibold text-blue-400">
                        {Math.round(caso.resultado.veredicto.culpa_a * 100)}%
                      </p>
                    </div>
                  </div>
                  <div className="w-px h-8 bg-zinc-800" />
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center">
                      <Car className="w-4 h-4 text-orange-400" />
                    </div>
                    <div>
                      <p className="text-[10px] text-zinc-500 uppercase">Vehicle B</p>
                      <p className="text-sm font-semibold text-orange-400">
                        {Math.round(caso.resultado.veredicto.culpa_b * 100)}%
                      </p>
                    </div>
                  </div>
                  <div className="w-px h-8 bg-zinc-800" />
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-[#C2E94B]/10 flex items-center justify-center">
                      <Activity className="w-4 h-4 text-[#C2E94B]" />
                    </div>
                    <div>
                      <p className="text-[10px] text-zinc-500 uppercase">Confidence</p>
                      <p className="text-sm font-semibold text-[#C2E94B]">
                        {Math.round(caso.resultado.veredicto.confidence * 100)}%
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Action buttons */}
              <div className="flex items-center gap-2">
                {caso.formulario_origen && (
                  <Button
                    variant="outline"
                    onClick={() => setShowFormulario(true)}
                    className="border-zinc-700 text-zinc-300 hover:text-white hover:border-zinc-600"
                  >
                    <ClipboardList className="w-4 h-4 mr-2" />
                    View Form
                  </Button>
                )}
                {caso.estado === "creado" && (
                  <Button
                    onClick={handleAnalizar}
                    className="bg-[#C2E94B] text-[#0a0a0a] hover:bg-[#d4f06d] font-medium"
                  >
                    <Zap className="w-4 h-4 mr-2" />
                    Analyze with AI
                  </Button>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Content area */}
        <div className="p-6">
          {/* Upload progress banner */}
          <UploadProgressBanner casoId={casoId} />

          <AnimatePresence mode="wait">
            {isProcessing ? (
              <motion.div
                key="processing"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="max-w-lg mx-auto py-16"
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
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                {/* Panel content */}
                <div className="bg-[#111] rounded-2xl border border-zinc-800/50 min-h-[calc(100vh-180px)] overflow-hidden">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={currentTab}
                      initial={{ opacity: 0, x: 10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -10 }}
                      transition={{ duration: 0.15 }}
                      className="h-full"
                    >
                      {currentTab === "informe" && (
                        <div className="p-6">
                          {informeLoading ? (
                            <div className="flex items-center justify-center py-20">
                              <div className="flex items-center gap-3 text-zinc-500">
                                <Loader2 className="w-5 h-5 animate-spin" />
                                <span>Loading report...</span>
                              </div>
                            </div>
                          ) : !informe ? (
                            <div className="flex flex-col items-center justify-center py-20">
                              <div className="w-20 h-20 rounded-2xl bg-zinc-800/50 flex items-center justify-center mb-6">
                                <FileText className="w-10 h-10 text-zinc-600" />
                              </div>
                              <h3 className="text-xl font-medium text-white mb-2">
                                Report not generated
                              </h3>
                              <p className="text-zinc-500 text-center max-w-md mb-8">
                                Generate the expert report draft with the case data.
                                Veridict will write it automatically.
                              </p>
                              <Button
                                onClick={handleRegenerarInforme}
                                disabled={informeRegenerating}
                                className="bg-[#C2E94B] text-[#0a0a0a] hover:bg-[#d4f06d] font-medium"
                              >
                                {informeRegenerating ? (
                                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                ) : (
                                  <Sparkles className="w-4 h-4 mr-2" />
                                )}
                                Generate report
                              </Button>
                            </div>
                          ) : (
                            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                              <div className="xl:col-span-2 space-y-6">
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-3">
                                    <h2 className="text-lg font-medium text-white">
                                      Expert Report
                                    </h2>
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      onClick={() => setPanelActivo("razonamiento")}
                                      className="border-[#C2E94B]/40 text-[#C2E94B] hover:bg-[#C2E94B]/10"
                                    >
                                      <Brain className="w-3.5 h-3.5 mr-2" />
                                      View orchestrator reasoning
                                    </Button>
                                  </div>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={handleRegenerarInforme}
                                    disabled={informeRegenerating}
                                    className="border-zinc-700 text-zinc-400 hover:text-white hover:border-zinc-600"
                                  >
                                    {informeRegenerating ? (
                                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    ) : (
                                      <RefreshCw className="w-4 h-4 mr-2" />
                                    )}
                                    Regenerate
                                  </Button>
                                </div>
                                <InformeDocumento
                                  informe={informe}
                                  caso={caso}
                                  onInformeUpdate={setInforme}
                                  recentlyEditedIds={recentlyEdited}
                                />
                              </div>
                              <div className="xl:col-span-1">
                                <div className="sticky top-24">
                                  <ChatInfoFaltante
                                    casoId={casoId}
                                    informe={informe}
                                    onUpdate={setInforme}
                                    onAffectedRespuestas={marcarRecentlyEdited}
                                  />
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {currentTab === "razonamiento" && (
                        <div className="p-6">
                          <RazonamientoOrquestadorView
                            casoId={casoId}
                            onNavigateToPanel={(panel) => setPanelActivo(panel)}
                          />
                        </div>
                      )}

                      {currentTab === "simulacion" && (
                        <div className="p-6 space-y-4">
                          <div className="flex items-center justify-between gap-3 flex-wrap">
                            <div className="flex flex-col gap-0.5">
                              <h3 className="text-sm font-semibold text-zinc-200">
                                Scene Reconstruction
                              </h3>
                              <p className="text-xs text-zinc-500">
                                {informe?.simulacion_escena?.actores?.length
                                  ? `${informe.simulacion_escena.actores.length} actor(s) · SimulationAgent (Opus 4.7)`
                                  : "No dynamic reconstruction generated for this case yet."}
                              </p>
                            </div>
                            <Button
                              onClick={regenerarSimulacion}
                              disabled={simulacionLoading || !informe}
                              variant="outline"
                              className="border-[#C2E94B]/30 text-[#C2E94B] hover:bg-[#C2E94B]/10"
                              title={!informe ? "Generate the report first" : "Reuse report data (fast)"}
                            >
                              {simulacionLoading ? (
                                <Loader2 className="w-3.5 h-3.5 mr-2 animate-spin" />
                              ) : (
                                <Sparkles className="w-3.5 h-3.5 mr-2" />
                              )}
                              {informe?.simulacion_escena?.actores?.length
                                ? "Regenerate simulation"
                                : "Generate simulation"}
                            </Button>
                          </div>
                          {simulacionError && (
                            <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 rounded px-3 py-2 font-mono">
                              ⚠ {simulacionError}
                            </div>
                          )}
                          <MapaReconstruccion
                            ubicacion={caso.ubicacion}
                            escenaSimulacion={informe?.simulacion_escena ?? undefined}
                            onGenerarSimulacion={regenerarSimulacion}
                            generandoSimulacion={simulacionLoading}
                          />
                          <SpecialistTrace
                            casoId={casoId}
                            tools={["generar_frame_simulacion", "obtener_frame_simulacion"]}
                            title="SimulationAgent Work"
                            description="Visual recreation of the accident: SVG sketches generated from velocities, masses, and positions validated by the PhysicsAgent."
                          />
                        </div>
                      )}

                      {currentTab === "cronologia" && (
                        <div className="p-6">
                          <Timeline
                            events={mapEventosToTimeline(caso.resultado?.cronologia ?? [])}
                            currentTime={currentTime}
                            onTimeChange={setCurrentTime}
                          />
                        </div>
                      )}

                      {currentTab === "calculos" && (
                        <div className="p-6 space-y-4">
                          <SpecialistTrace
                            casoId={casoId}
                            tools={["calcular_fisica", "simular_fisica", "analizar_biomecanica"]}
                            title="PhysicsAgent and BiomechanicsAgent Work"
                            description="Deterministic physics calculations (Stannard-Baker, momentum balance, stopping distance, kinetic energy) and biomechanical patterns (WAD, AIS) cited by the orchestrator to infer velocities and injury compatibility."
                          />
                          <CalculosFisicos calculos={caso.resultado?.calculos || []} />
                        </div>
                      )}

                      {currentTab === "legal" && (
                        <div className="p-6 space-y-4">
                          <SpecialistTrace
                            casoId={casoId}
                            tools={["consultar_legal"]}
                            title="LegalAgent Work"
                            description="RGC/LSV/RGV articles consulted from the BOE and jurisprudence cited by the legal specialist."
                          />
                          <RazonamientoLegal
                            infracciones={caso.resultado?.infracciones || []}
                            veredicto={caso.resultado?.veredicto}
                          />
                        </div>
                      )}

                      {currentTab === "confrontacion" && (
                        <div className="p-6 space-y-4">
                          <SpecialistTrace
                            casoId={casoId}
                            tools={["verificar_atestado", "analizar_conformidad_atestado"]}
                            title="AtestadoAgent and ConformidadAgent Work"
                            description="Verification of inconsistencies between report versions and physical evidence, and procedural compliance analysis."
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

                      {currentTab === "contexto" && (
                        <div className="p-6 space-y-4">
                          <SpecialistTrace
                            casoId={casoId}
                            tools={["consultar_meteo"]}
                            title="MeteoAgent Work"
                            description="Historical weather data (Open-Meteo) and solar position (glare) at the time of the accident."
                          />
                          <ContextoPanel contexto={caso.resultado?.contexto ?? caso.contexto} />
                        </div>
                      )}

                      {currentTab === "vehiculos" && (
                        <div className="p-6 space-y-4">
                          <SpecialistTrace
                            casoId={casoId}
                            tools={["consultar_ficha_tecnica"]}
                            title="FichaAgent Work"
                            description="Complete technical sheet for each vehicle (mass, dimensions, rigidity, safety systems) consulted by the specialist."
                          />
                          <VehiculosPanel vehiculos={caso.vehiculos ?? []} />
                        </div>
                      )}

                      {currentTab === "escena" && (
                        <div className="p-6 space-y-4">
                          <SpecialistTrace
                            casoId={casoId}
                            tools={["consultar_escena"]}
                            title="SceneAgent Work"
                            description="Road geometry (OSM Overpass), signage, slope (DEM), and ground-level images (Mapillary) collected by the specialist."
                          />
                          <EscenaPanel escena={caso.escena} />
                        </div>
                      )}

                      {currentTab === "docs" && (
                        <div className="p-6 space-y-4">
                          <SpecialistTrace
                            casoId={casoId}
                            tools={[
                              "listar_biblioteca_fotos",
                              "buscar_foto_perito",
                              "analizar_imagen_dano",
                            ]}
                            title="Photo Library and Vision Work"
                            description="Claude vision indexing of the case photo library and damage analysis on specific photographs requested by the orchestrator."
                          />
                          <DocumentosPanel
                            documentos={caso.documentos ?? []}
                            fotos={caso.fotos ?? []}
                          />
                        </div>
                      )}
                    </motion.div>
                  </AnimatePresence>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* Modal: View original form */}
      {showFormulario && caso.formulario_origen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
          onClick={() => setShowFormulario(false)}
        >
          <div
            className="bg-[#111] border border-zinc-700 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[85vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800">
              <div className="flex items-center gap-2">
                <ClipboardList className="w-5 h-5 text-[#C2E94B]" />
                <h3 className="text-white font-medium">Original Case Form</h3>
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
                  className="text-zinc-400 hover:text-white"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download JSON
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    navigator.clipboard.writeText(
                      JSON.stringify(caso.formulario_origen, null, 2),
                    );
                    toast.success("Copied", "Form JSON copied to clipboard.");
                  }}
                  className="text-zinc-400 hover:text-white"
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Copy
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
