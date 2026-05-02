"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import {
  Play,
  FileText,
  Brain,
  Scale,
  Shield,
  CheckCircle2,
  AlertTriangle,
  Download,
  RotateCcw,
  Zap,
  Car,
  ChevronRight,
  Eye,
  Clock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

// Tipos para los agentes
interface AgentThought {
  text: string;
  type: "thinking" | "finding" | "warning" | "success";
}

interface AgentStatus {
  id: string;
  name: string;
  icon: React.ReactNode;
  color: string;
  status: "idle" | "thinking" | "done" | "error";
  progress: number;
  thoughts: AgentThought[];
  result?: string;
}

// Datos del caso demo
const demoCase = {
  id: "DEMO-2026-001",
  title: "Colisión lateral M-30 km 12.5",
  date: "15 de Abril de 2026, 14:30h",
  location: "Madrid, M-30 km 12.5",
  weather: "Lluvia intensa",
  type: "Colisión lateral con cambio de carril",
  documents: [
    { name: "Atestado Policial", pages: 12, size: "2.4 MB" },
    { name: "Parte Amistoso", pages: 2, size: "340 KB" },
    { name: "Informe Meteo AEMET", pages: 1, size: "120 KB" },
  ],
  photos: 8,
};

// Simulación del procesamiento por agente
const agentSimulation: { agent: string; thoughts: AgentThought[]; duration: number; result: string }[] = [
  {
    agent: "extractor",
    duration: 4000,
    result: "3 documentos procesados, 8 fotos analizadas",
    thoughts: [
      { text: "Iniciando OCR del atestado policial...", type: "thinking" },
      { text: "Detectando vehículos: Seat León (A), BMW Serie 3 (B)", type: "finding" },
      { text: "Extrayendo declaraciones de conductores...", type: "thinking" },
      { text: "Procesando 8 fotografías con Vision AI...", type: "thinking" },
      { text: "Daños detectados: frontal derecho (A), lateral izquierdo (B)", type: "finding" },
      { text: "Consultando datos AEMET: lluvia 12mm/h, visibilidad reducida", type: "finding" },
      { text: "Extracción completada ✓", type: "success" },
    ],
  },
  {
    agent: "reconstructor",
    duration: 5000,
    result: "V₀=67.3 km/h | EBS=45.2 km/h | Frenada=12.5m",
    thoughts: [
      { text: "Analizando huellas de frenada: 12.5m detectados", type: "thinking" },
      { text: "Aplicando fórmula Stannard-Baker...", type: "thinking" },
      { text: "μ = 0.65 (asfalto mojado según AEMET)", type: "finding" },
      { text: "V₀ = √(2 × 0.65 × 9.81 × 12.5) = 67.3 km/h", type: "finding" },
      { text: "Calculando EBS por deformación (CRASH3)...", type: "thinking" },
      { text: "Deformación media: 23cm → EBS = 45.2 km/h", type: "finding" },
      { text: "Aplicando conservación momento lineal...", type: "thinking" },
      { text: "⚠️ Velocidad A superior al límite (50 km/h)", type: "warning" },
      { text: "Cálculos verificados ✓", type: "success" },
    ],
  },
  {
    agent: "legal",
    duration: 4000,
    result: "2 infracciones detectadas con citas BOE",
    thoughts: [
      { text: "Consultando RAG corpus legal español...", type: "thinking" },
      { text: "Analizando Art. 74.1 RGC (límites de velocidad)...", type: "thinking" },
      { text: "INFRACCIÓN: Vehículo A circulaba a 67 km/h en zona de 50", type: "warning" },
      { text: "Fuente: BOE-A-2003-23514", type: "finding" },
      { text: "Analizando Art. 72.1 RGC (cambio de carril)...", type: "thinking" },
      { text: "INFRACCIÓN: Vehículo B no señalizó maniobra", type: "warning" },
      { text: "Buscando jurisprudencia aplicable...", type: "thinking" },
      { text: "STS 1234/2024: caso precedente similar", type: "finding" },
      { text: "Análisis legal completado ✓", type: "success" },
    ],
  },
  {
    agent: "adversarial",
    duration: 3500,
    result: "1 contradicción detectada en versión conductor B",
    thoughts: [
      { text: "Iniciando verificación adversarial...", type: "thinking" },
      { text: "Comparando versión conductor A con evidencia física...", type: "thinking" },
      { text: "Versión A: COMPATIBLE con huellas de frenada ✓", type: "success" },
      { text: "Comparando versión conductor B con evidencia física...", type: "thinking" },
      { text: "⚠️ CONTRADICCIÓN DETECTADA", type: "warning" },
      { text: "B declara: \"iba a 50 km/h\"", type: "finding" },
      { text: "Evidencia física: deformación indica 55+ km/h", type: "warning" },
      { text: "Verificando coherencia temporal...", type: "thinking" },
      { text: "Verificación adversarial completada ✓", type: "success" },
    ],
  },
];

// Componente de pensamiento del agente con efecto typewriter
function ThoughtBubble({ thought, isLatest }: { thought: AgentThought; isLatest: boolean }) {
  const [displayText, setDisplayText] = useState("");
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!isLatest) {
      setDisplayText(thought.text);
      setIsComplete(true);
      return;
    }

    let index = 0;
    const timer = setInterval(() => {
      if (index < thought.text.length) {
        setDisplayText(thought.text.slice(0, index + 1));
        index++;
      } else {
        setIsComplete(true);
        clearInterval(timer);
      }
    }, 20);

    return () => clearInterval(timer);
  }, [thought.text, isLatest]);

  const colors = {
    thinking: "text-veridict-gray",
    finding: "text-blue-400",
    warning: "text-amber-400",
    success: "text-veridict-lime",
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={`text-sm font-mono ${colors[thought.type]} ${isLatest && !isComplete ? "border-r-2 border-current" : ""}`}
    >
      {thought.type === "warning" && "⚠️ "}
      {thought.type === "success" && "✓ "}
      {thought.type === "finding" && "→ "}
      {displayText}
    </motion.div>
  );
}

// Componente del Agente
function AgentCard({ agent, isActive }: { agent: AgentStatus; isActive: boolean }) {
  return (
    <motion.div
      layout
      className={`p-4 rounded-xl border transition-all duration-300 ${
        agent.status === "done"
          ? "border-veridict-lime/40 bg-veridict-lime/5"
          : agent.status === "thinking"
          ? "border-veridict-lime/60 bg-veridict-green-800/80 shadow-[0_0_30px_rgba(194,233,75,0.15)]"
          : agent.status === "error"
          ? "border-red-500/40 bg-red-500/5"
          : "border-veridict-green-600 bg-veridict-green-800/50 opacity-50"
      }`}
    >
      <div className="flex items-center gap-3 mb-3">
        <div
          className={`p-2 rounded-lg transition-colors ${
            agent.status === "thinking"
              ? "bg-veridict-lime/20 text-veridict-lime"
              : agent.status === "done"
              ? "bg-veridict-lime/30 text-veridict-lime"
              : "bg-veridict-green-700 text-veridict-gray"
          }`}
        >
          {agent.icon}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-medium text-veridict-white">{agent.name}</span>
            {agent.status === "thinking" && (
              <motion.div
                className="w-2 h-2 rounded-full bg-veridict-lime"
                animate={{ scale: [1, 1.3, 1], opacity: [1, 0.5, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
              />
            )}
            {agent.status === "done" && (
              <CheckCircle2 className="w-4 h-4 text-veridict-lime" />
            )}
          </div>
          {agent.status === "thinking" && (
            <Progress value={agent.progress} className="h-1 mt-1" />
          )}
        </div>
      </div>

      {/* Pensamientos del agente */}
      {(agent.status === "thinking" || agent.status === "done") && (
        <div className="space-y-1 max-h-32 overflow-y-auto">
          {agent.thoughts.slice(-5).filter(Boolean).map((thought, idx) => (
            <ThoughtBubble
              key={idx}
              thought={thought}
              isLatest={idx === agent.thoughts.filter(Boolean).length - 1 && agent.status === "thinking"}
            />
          ))}
        </div>
      )}

      {/* Resultado final */}
      {agent.status === "done" && agent.result && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 pt-3 border-t border-veridict-green-600"
        >
          <div className="text-xs text-veridict-gray mb-1">Resultado:</div>
          <div className="text-sm font-mono text-veridict-lime">{agent.result}</div>
        </motion.div>
      )}
    </motion.div>
  );
}

// Componente del resultado final
function ResultsPanel({ visible }: { visible: boolean }) {
  if (!visible) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header del dictamen */}
      <div className="text-center py-4">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", delay: 0.2 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-veridict-lime/20 text-veridict-lime mb-4"
        >
          <CheckCircle2 className="w-5 h-5" />
          Análisis Completado
        </motion.div>
        <h2 className="text-2xl font-bold text-veridict-white">Dictamen Pericial</h2>
        <p className="text-veridict-gray">Formato UNE-EN 16775 • Verificado por IA</p>
      </div>

      {/* Veredicto principal */}
      <Card className="p-6 bg-gradient-to-br from-veridict-green-800/80 to-veridict-green-900/80">
        <h3 className="text-lg font-semibold text-veridict-white mb-4 flex items-center gap-2">
          <Scale className="w-5 h-5 text-veridict-lime" />
          Atribución de Responsabilidad
        </h3>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <motion.div
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30 text-center"
          >
            <div className="text-sm text-blue-400 mb-1">Vehículo A</div>
            <div className="text-4xl font-bold text-blue-400">65%</div>
            <div className="text-xs text-blue-400/70 mt-1">Exceso de velocidad</div>
          </motion.div>
          <motion.div
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/30 text-center"
          >
            <div className="text-sm text-orange-400 mb-1">Vehículo B</div>
            <div className="text-4xl font-bold text-orange-400">35%</div>
            <div className="text-xs text-orange-400/70 mt-1">Cambio sin señalizar</div>
          </motion.div>
        </div>
        <div className="flex justify-center">
          <Badge className="bg-veridict-lime/20 text-veridict-lime border-veridict-lime/40">
            Confianza del modelo: 89%
          </Badge>
        </div>
      </Card>

      {/* Contradicción detectada - EL MOMENTO WOW */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Card className="p-6 border-amber-500/40 bg-amber-500/5">
          <h3 className="text-lg font-semibold text-amber-400 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Contradicción Detectada por Devil's Advocate
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 rounded-lg bg-veridict-green-800 border border-veridict-green-600">
              <div className="text-xs text-veridict-gray mb-1">Versión Conductor B:</div>
              <div className="text-sm text-veridict-white">"Circulaba a 50 km/h respetando el límite"</div>
            </div>
            <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30">
              <div className="text-xs text-amber-400 mb-1">Evidencia Física:</div>
              <div className="text-sm text-amber-400">Deformación indica velocidad de 55+ km/h</div>
            </div>
          </div>
          <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30">
            <div className="text-sm text-red-400 font-medium">
              ⚠️ La versión del conductor B es INCOMPATIBLE con la evidencia física analizada
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Acciones */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="flex gap-4 justify-center"
      >
        <Button size="lg" className="gap-2">
          <Download className="w-5 h-5" />
          Descargar Dictamen PDF
        </Button>
        <Link href="/casos/1">
          <Button variant="outline" size="lg" className="gap-2">
            <Eye className="w-5 h-5" />
            Ver Análisis Completo
          </Button>
        </Link>
      </motion.div>

      {/* Hash Sigstore */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="text-center"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-veridict-green-800 border border-veridict-green-600">
          <Shield className="w-4 h-4 text-veridict-lime" />
          <span className="text-xs text-veridict-gray">Sigstore Hash:</span>
          <code className="text-xs text-veridict-lime font-mono">sha256:7f8a9b2c...4e5d</code>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default function DemoPage() {
  const [stage, setStage] = useState<"intro" | "processing" | "results">("intro");
  const [currentAgentIndex, setCurrentAgentIndex] = useState(0);
  const [agents, setAgents] = useState<AgentStatus[]>([
    { id: "extractor", name: "Extractor", icon: <FileText className="w-5 h-5" />, color: "blue", status: "idle", progress: 0, thoughts: [] },
    { id: "reconstructor", name: "Reconstructor", icon: <Car className="w-5 h-5" />, color: "purple", status: "idle", progress: 0, thoughts: [] },
    { id: "legal", name: "Legal", icon: <Scale className="w-5 h-5" />, color: "amber", status: "idle", progress: 0, thoughts: [] },
    { id: "adversarial", name: "Devil's Advocate", icon: <Shield className="w-5 h-5" />, color: "red", status: "idle", progress: 0, thoughts: [] },
  ]);
  const thoughtIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const startAnalysis = () => {
    setStage("processing");
    setCurrentAgentIndex(0);
    setAgents(prev => prev.map(a => ({ ...a, status: "idle", progress: 0, thoughts: [] })));
    processAgent(0);
  };

  const processAgent = (index: number) => {
    if (index >= agentSimulation.length) {
      setStage("results");
      return;
    }

    const sim = agentSimulation[index];
    const thoughtDelay = sim.duration / sim.thoughts.length;
    let thoughtIndex = 0;

    // Marcar agente como activo
    setAgents(prev => prev.map((a, i) =>
      i === index ? { ...a, status: "thinking", progress: 0 } : a
    ));

    // Simular pensamientos
    thoughtIntervalRef.current = setInterval(() => {
      if (thoughtIndex < sim.thoughts.length) {
        setAgents(prev => prev.map((a, i) =>
          i === index
            ? { ...a, thoughts: [...a.thoughts, sim.thoughts[thoughtIndex]] }
            : a
        ));
        thoughtIndex++;
      }
    }, thoughtDelay);

    // Simular progreso
    const progressStep = 100 / (sim.duration / 100);
    progressIntervalRef.current = setInterval(() => {
      setAgents(prev => {
        const agent = prev[index];
        if (agent.progress >= 100) {
          return prev;
        }
        return prev.map((a, i) =>
          i === index ? { ...a, progress: Math.min(a.progress + progressStep, 100) } : a
        );
      });
    }, 100);

    // Finalizar agente y pasar al siguiente
    setTimeout(() => {
      if (thoughtIntervalRef.current) clearInterval(thoughtIntervalRef.current);
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);

      setAgents(prev => prev.map((a, i) =>
        i === index ? { ...a, status: "done", progress: 100, result: sim.result } : a
      ));

      setCurrentAgentIndex(index + 1);
      setTimeout(() => processAgent(index + 1), 500);
    }, sim.duration);
  };

  const resetDemo = () => {
    if (thoughtIntervalRef.current) clearInterval(thoughtIntervalRef.current);
    if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
    setStage("intro");
    setCurrentAgentIndex(0);
    setAgents(prev => prev.map(a => ({ ...a, status: "idle", progress: 0, thoughts: [] })));
  };

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <Badge className="mb-4 bg-veridict-lime/20 text-veridict-lime border-veridict-lime/40">
            Demo Interactivo
          </Badge>
          <h1 className="text-4xl font-bold text-veridict-white mb-2">
            Veridict AI en Acción
          </h1>
          <p className="text-veridict-gray max-w-2xl mx-auto">
            Observa cómo 4 agentes de IA especializados analizan un accidente de tráfico
            y generan un dictamen pericial verificable en tiempo real.
          </p>
        </div>

        {/* Main content */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Panel izquierdo - Caso */}
          <div>
            <Card className="p-6 h-full">
              <h2 className="text-lg font-semibold text-veridict-white mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-veridict-lime" />
                Caso: {demoCase.id}
              </h2>

              {/* Info del caso */}
              <div className="space-y-4 mb-6">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-veridict-gray">Fecha:</span>
                    <div className="text-veridict-white">{demoCase.date}</div>
                  </div>
                  <div>
                    <span className="text-veridict-gray">Ubicación:</span>
                    <div className="text-veridict-white">{demoCase.location}</div>
                  </div>
                  <div>
                    <span className="text-veridict-gray">Condiciones:</span>
                    <div className="text-amber-400">{demoCase.weather}</div>
                  </div>
                  <div>
                    <span className="text-veridict-gray">Tipo:</span>
                    <div className="text-veridict-white">{demoCase.type}</div>
                  </div>
                </div>
              </div>

              {/* Documentos */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-veridict-gray mb-3">Documentos adjuntos:</h3>
                <div className="space-y-2">
                  {demoCase.documents.map((doc, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-3 rounded-lg bg-veridict-green-800 border border-veridict-green-600"
                    >
                      <div className="flex items-center gap-3">
                        <FileText className="w-4 h-4 text-veridict-lime" />
                        <span className="text-sm text-veridict-white">{doc.name}</span>
                      </div>
                      <span className="text-xs text-veridict-gray">{doc.pages} págs • {doc.size}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Fotos */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-veridict-gray mb-3">Fotografías:</h3>
                <div className="grid grid-cols-4 gap-2">
                  {[...Array(demoCase.photos)].map((_, idx) => (
                    <div
                      key={idx}
                      className="aspect-square rounded-lg bg-veridict-green-700 border border-veridict-green-600 flex items-center justify-center"
                    >
                      <Car className={`w-6 h-6 ${idx < 4 ? "text-blue-400" : "text-orange-400"}`} />
                    </div>
                  ))}
                </div>
              </div>

              {/* Botón de acción */}
              {stage === "intro" && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <Button
                    size="lg"
                    className="w-full text-lg py-6 gap-2"
                    onClick={startAnalysis}
                  >
                    <Play className="w-6 h-6" />
                    Iniciar Análisis con IA
                  </Button>
                </motion.div>
              )}

              {stage === "processing" && (
                <div className="flex items-center justify-center gap-3 py-4">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  >
                    <Brain className="w-6 h-6 text-veridict-lime" />
                  </motion.div>
                  <span className="text-veridict-lime font-medium">Procesando...</span>
                </div>
              )}

              {stage === "results" && (
                <Button
                  variant="outline"
                  className="w-full gap-2"
                  onClick={resetDemo}
                >
                  <RotateCcw className="w-4 h-4" />
                  Reiniciar Demo
                </Button>
              )}
            </Card>
          </div>

          {/* Panel derecho - Pipeline o Resultados */}
          <div>
            <AnimatePresence mode="wait">
              {stage === "intro" && (
                <motion.div
                  key="intro"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <Card className="p-6 h-full flex flex-col items-center justify-center text-center">
                    <motion.div
                      animate={{ scale: [1, 1.05, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      <Brain className="w-16 h-16 text-veridict-lime/30 mb-6" />
                    </motion.div>
                    <h3 className="text-xl font-semibold text-veridict-white mb-2">
                      Pipeline de IA Forense
                    </h3>
                    <p className="text-veridict-gray mb-6 max-w-md">
                      4 agentes especializados trabajarán en secuencia para analizar
                      el caso y generar un dictamen pericial completo.
                    </p>
                    <div className="flex items-center gap-3 text-sm text-veridict-gray">
                      <Clock className="w-4 h-4" />
                      Tiempo estimado: ~20 segundos
                    </div>
                  </Card>
                </motion.div>
              )}

              {stage === "processing" && (
                <motion.div
                  key="processing"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-4"
                >
                  {agents.map((agent, idx) => (
                    <AgentCard key={agent.id} agent={agent} isActive={idx === currentAgentIndex} />
                  ))}
                </motion.div>
              )}

              {stage === "results" && (
                <motion.div
                  key="results"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <ResultsPanel visible={true} />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Footer info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-12 text-center"
        >
          <div className="inline-flex items-center gap-6 text-sm text-veridict-gray">
            <span className="flex items-center gap-1">
              <Zap className="w-4 h-4 text-veridict-lime" />
              Powered by Claude AI
            </span>
            <span>•</span>
            <span>Cumple UNE-EN 16775</span>
            <span>•</span>
            <span>Trazabilidad Sigstore</span>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
