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

// Types for the agents
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

// Demo case data
const demoCase = {
  id: "DEMO-2026-001",
  title: "Lateral collision M-30 km 12.5",
  date: "April 15, 2026, 2:30 PM",
  location: "Madrid, M-30 km 12.5",
  weather: "Heavy rain",
  type: "Lateral collision with lane change",
  documents: [
    { name: "Police Report", pages: 12, size: "2.4 MB" },
    { name: "Accident Report Form", pages: 2, size: "340 KB" },
    { name: "AEMET Weather Report", pages: 1, size: "120 KB" },
  ],
  photos: 8,
};

// Agent processing simulation
const agentSimulation: { agent: string; thoughts: AgentThought[]; duration: number; result: string }[] = [
  {
    agent: "extractor",
    duration: 4000,
    result: "3 documents processed, 8 photos analyzed",
    thoughts: [
      { text: "Starting OCR on police report...", type: "thinking" },
      { text: "Detecting vehicles: Seat León (A), BMW 3 Series (B)", type: "finding" },
      { text: "Extracting driver statements...", type: "thinking" },
      { text: "Processing 8 photos with Vision AI...", type: "thinking" },
      { text: "Damage detected: front right (A), left side (B)", type: "finding" },
      { text: "Querying AEMET data: rain 12mm/h, reduced visibility", type: "finding" },
      { text: "Extraction completed ✓", type: "success" },
    ],
  },
  {
    agent: "reconstructor",
    duration: 5000,
    result: "V₀=67.3 km/h | EBS=45.2 km/h | Braking=12.5m",
    thoughts: [
      { text: "Analyzing skid marks: 12.5m detected", type: "thinking" },
      { text: "Applying Stannard-Baker formula...", type: "thinking" },
      { text: "μ = 0.65 (wet asphalt per AEMET)", type: "finding" },
      { text: "V₀ = √(2 × 0.65 × 9.81 × 12.5) = 67.3 km/h", type: "finding" },
      { text: "Calculating EBS from deformation (CRASH3)...", type: "thinking" },
      { text: "Average deformation: 23cm → EBS = 45.2 km/h", type: "finding" },
      { text: "Applying linear momentum conservation...", type: "thinking" },
      { text: "⚠️ Vehicle A speed exceeds limit (50 km/h)", type: "warning" },
      { text: "Calculations verified ✓", type: "success" },
    ],
  },
  {
    agent: "legal",
    duration: 4000,
    result: "2 violations detected with BOE citations",
    thoughts: [
      { text: "Querying Spanish legal RAG corpus...", type: "thinking" },
      { text: "Analyzing Art. 74.1 RGC (speed limits)...", type: "thinking" },
      { text: "VIOLATION: Vehicle A traveling at 67 km/h in 50 zone", type: "warning" },
      { text: "Source: BOE-A-2003-23514", type: "finding" },
      { text: "Analyzing Art. 72.1 RGC (lane change)...", type: "thinking" },
      { text: "VIOLATION: Vehicle B did not signal maneuver", type: "warning" },
      { text: "Searching applicable case law...", type: "thinking" },
      { text: "STS 1234/2024: similar precedent case", type: "finding" },
      { text: "Legal analysis completed ✓", type: "success" },
    ],
  },
  {
    agent: "adversarial",
    duration: 3500,
    result: "1 contradiction detected in driver B's version",
    thoughts: [
      { text: "Starting adversarial verification...", type: "thinking" },
      { text: "Comparing driver A's version with physical evidence...", type: "thinking" },
      { text: "Version A: COMPATIBLE with skid marks ✓", type: "success" },
      { text: "Comparing driver B's version with physical evidence...", type: "thinking" },
      { text: "⚠️ CONTRADICTION DETECTED", type: "warning" },
      { text: "B states: \"I was going 50 km/h\"", type: "finding" },
      { text: "Physical evidence: deformation indicates 55+ km/h", type: "warning" },
      { text: "Verifying temporal coherence...", type: "thinking" },
      { text: "Adversarial verification completed ✓", type: "success" },
    ],
  },
];

// Agent thought component with typewriter effect
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

// Agent Component
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

      {/* Agent thoughts */}
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

      {/* Final result */}
      {agent.status === "done" && agent.result && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 pt-3 border-t border-veridict-green-600"
        >
          <div className="text-xs text-veridict-gray mb-1">Result:</div>
          <div className="text-sm font-mono text-veridict-lime">{agent.result}</div>
        </motion.div>
      )}
    </motion.div>
  );
}

// Final result component
function ResultsPanel({ visible }: { visible: boolean }) {
  if (!visible) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Verdict header */}
      <div className="text-center py-4">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", delay: 0.2 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-veridict-lime/20 text-veridict-lime mb-4"
        >
          <CheckCircle2 className="w-5 h-5" />
          Analysis Complete
        </motion.div>
        <h2 className="text-2xl font-bold text-veridict-white">Expert Report</h2>
        <p className="text-veridict-gray">UNE-EN 16775 Format • AI Verified</p>
      </div>

      {/* Main verdict */}
      <Card className="p-6 bg-gradient-to-br from-veridict-green-800/80 to-veridict-green-900/80">
        <h3 className="text-lg font-semibold text-veridict-white mb-4 flex items-center gap-2">
          <Scale className="w-5 h-5 text-veridict-lime" />
          Liability Attribution
        </h3>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <motion.div
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30 text-center"
          >
            <div className="text-sm text-blue-400 mb-1">Vehicle A</div>
            <div className="text-4xl font-bold text-blue-400">65%</div>
            <div className="text-xs text-blue-400/70 mt-1">Speeding</div>
          </motion.div>
          <motion.div
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/30 text-center"
          >
            <div className="text-sm text-orange-400 mb-1">Vehicle B</div>
            <div className="text-4xl font-bold text-orange-400">35%</div>
            <div className="text-xs text-orange-400/70 mt-1">Unsignaled lane change</div>
          </motion.div>
        </div>
        <div className="flex justify-center">
          <Badge className="bg-veridict-lime/20 text-veridict-lime border-veridict-lime/40">
            Model confidence: 89%
          </Badge>
        </div>
      </Card>

      {/* Contradiction detected - THE WOW MOMENT */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Card className="p-6 border-amber-500/40 bg-amber-500/5">
          <h3 className="text-lg font-semibold text-amber-400 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Contradiction Detected by Devil's Advocate
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 rounded-lg bg-veridict-green-800 border border-veridict-green-600">
              <div className="text-xs text-veridict-gray mb-1">Driver B's Version:</div>
              <div className="text-sm text-veridict-white">"I was going 50 km/h respecting the limit"</div>
            </div>
            <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30">
              <div className="text-xs text-amber-400 mb-1">Physical Evidence:</div>
              <div className="text-sm text-amber-400">Deformation indicates speed of 55+ km/h</div>
            </div>
          </div>
          <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30">
            <div className="text-sm text-red-400 font-medium">
              ⚠️ Driver B's version is INCOMPATIBLE with the analyzed physical evidence
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Actions */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="flex gap-4 justify-center"
      >
        <Button size="lg" className="gap-2">
          <Download className="w-5 h-5" />
          Download Expert Report PDF
        </Button>
        <Link href="/casos">
          <Button variant="outline" size="lg" className="gap-2">
            <Eye className="w-5 h-5" />
            View Full Analysis
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
            Interactive Demo
          </Badge>
          <h1 className="text-4xl font-bold text-veridict-white mb-2">
            Veridict AI in Action
          </h1>
          <p className="text-veridict-gray max-w-2xl mx-auto">
            Watch how 4 specialized AI agents analyze a traffic accident
            and generate a verifiable expert report in real time.
          </p>
        </div>

        {/* Main content */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left panel - Case */}
          <div>
            <Card className="p-6 h-full">
              <h2 className="text-lg font-semibold text-veridict-white mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-veridict-lime" />
                Caso: {demoCase.id}
              </h2>

              {/* Case info */}
              <div className="space-y-4 mb-6">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-veridict-gray">Date:</span>
                    <div className="text-veridict-white">{demoCase.date}</div>
                  </div>
                  <div>
                    <span className="text-veridict-gray">Location:</span>
                    <div className="text-veridict-white">{demoCase.location}</div>
                  </div>
                  <div>
                    <span className="text-veridict-gray">Conditions:</span>
                    <div className="text-amber-400">{demoCase.weather}</div>
                  </div>
                  <div>
                    <span className="text-veridict-gray">Type:</span>
                    <div className="text-veridict-white">{demoCase.type}</div>
                  </div>
                </div>
              </div>

              {/* Documents */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-veridict-gray mb-3">Attached documents:</h3>
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
                      <span className="text-xs text-veridict-gray">{doc.pages} pages • {doc.size}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Photos */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-veridict-gray mb-3">Photographs:</h3>
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

              {/* Action button */}
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
                    Start AI Analysis
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
                  <span className="text-veridict-lime font-medium">Processing...</span>
                </div>
              )}

              {stage === "results" && (
                <Button
                  variant="outline"
                  className="w-full gap-2"
                  onClick={resetDemo}
                >
                  <RotateCcw className="w-4 h-4" />
                  Reset Demo
                </Button>
              )}
            </Card>
          </div>

          {/* Right panel - Pipeline or Results */}
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
                      Forensic AI Pipeline
                    </h3>
                    <p className="text-veridict-gray mb-6 max-w-md">
                      4 specialized agents will work in sequence to analyze
                      the case and generate a complete expert report.
                    </p>
                    <div className="flex items-center gap-3 text-sm text-veridict-gray">
                      <Clock className="w-4 h-4" />
                      Estimated time: ~20 seconds
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

        {/* Footer */}
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
            <span>UNE-EN 16775 Compliant</span>
            <span>•</span>
            <span>Sigstore Traceability</span>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
