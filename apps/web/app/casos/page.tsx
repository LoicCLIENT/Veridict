"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { api, type Caso } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import {
  FileText,
  Clock,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Plus,
  Brain,
  ArrowLeft,
  ArrowRight,
  Database,
  Sparkles,
  MapPin,
} from "lucide-react";

export default function CasosPage() {
  const [casos, setCasos] = useState<Caso[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  const loadCasos = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getCasos();
      setCasos(data);
    } catch (e) {
      console.error("Error loading casos:", e);
      const msg = "Could not connect to backend.";
      setError(msg);
      toast.error("Network error", msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCasos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const estadoConfig = (estado: Caso["estado"]) => {
    switch (estado) {
      case "creado":
        return {
          label: "Pending",
          icon: <FileText className="w-3.5 h-3.5" />,
          dot: "bg-zinc-500",
          text: "text-zinc-400",
          ring: "ring-zinc-700/40",
        };
      case "procesando":
        return {
          label: "Processing",
          icon: <Clock className="w-3.5 h-3.5 animate-spin" />,
          dot: "bg-[#C2E94B]",
          text: "text-[#C2E94B]",
          ring: "ring-[#C2E94B]/30",
        };
      case "completado":
        return {
          label: "Completed",
          icon: <CheckCircle2 className="w-3.5 h-3.5" />,
          dot: "bg-emerald-400",
          text: "text-emerald-400",
          ring: "ring-emerald-500/30",
        };
      case "escalado_humano":
        return {
          label: "Review",
          icon: <AlertTriangle className="w-3.5 h-3.5" />,
          dot: "bg-amber-400",
          text: "text-amber-400",
          ring: "ring-amber-500/30",
        };
    }
  };

  const tipoLabel = (tipo: Caso["tipo_colision"]) => {
    const labels = {
      frontal: "Frontal",
      lateral: "Side impact",
      alcance: "Rear-end",
      atropello: "Pedestrian hit",
    };
    return labels[tipo];
  };

  const completados = casos.filter((c) => c.estado === "completado").length;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Top nav */}
      <header className="sticky top-0 z-30 bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-zinc-800/50">
        <div className="max-w-7xl mx-auto flex items-center justify-between h-16 px-6">
          <Link href="/" className="flex items-center gap-3">
            <img src="/logo.png" alt="Veridict" className="h-8 w-auto" />
          </Link>
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to home
          </Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-10">
        {/* Hero — learning message */}
        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="relative overflow-hidden rounded-3xl border border-zinc-800/60 bg-gradient-to-br from-[#111] via-[#0d0d0d] to-[#0a0a0a] p-8 md:p-12 mb-10"
        >
          {/* Decorative glow */}
          <div className="absolute -top-32 -right-32 w-96 h-96 bg-[#C2E94B]/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -left-24 w-80 h-80 bg-[#C2E94B]/5 rounded-full blur-3xl pointer-events-none" />

          <div className="relative grid md:grid-cols-[1fr_auto] gap-8 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#C2E94B]/10 border border-[#C2E94B]/20 text-[#C2E94B] text-xs font-medium mb-5">
                <Sparkles className="w-3.5 h-3.5" />
                Continuous learning
              </div>
              <h1 className="text-3xl md:text-5xl font-semibold tracking-tight text-white leading-[1.05]">
                Store your cases.{" "}
                <span className="text-[#C2E94B]">
                  Let the model learn from them.
                </span>
              </h1>
              <p className="mt-5 text-zinc-400 text-base md:text-lg max-w-2xl leading-relaxed">
                Every case you analyze with Veridict feeds the agents with new
                evidence patterns, expert reasoning, and verified verdicts. The
                more cases stored, the sharper the forensic intelligence becomes.
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-3">
                <Link href="/casos/nuevo">
                  <Button className="bg-[#C2E94B] text-[#0a0a0a] hover:bg-[#d4f06d] font-medium h-11 px-5">
                    <Plus className="w-4 h-4 mr-2" />
                    New case
                  </Button>
                </Link>
                <Button
                  variant="outline"
                  onClick={loadCasos}
                  className="border-zinc-700 bg-transparent text-zinc-300 hover:text-white hover:border-zinc-600 h-11 px-5"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-3 md:min-w-[280px]">
              <div className="rounded-2xl border border-zinc-800/60 bg-black/40 p-5">
                <div className="flex items-center gap-2 text-zinc-500 text-xs uppercase tracking-wider mb-2">
                  <Database className="w-3.5 h-3.5" />
                  Stored
                </div>
                <p className="text-3xl font-semibold text-white tabular-nums">
                  {casos.length}
                </p>
              </div>
              <div className="rounded-2xl border border-zinc-800/60 bg-black/40 p-5">
                <div className="flex items-center gap-2 text-zinc-500 text-xs uppercase tracking-wider mb-2">
                  <Brain className="w-3.5 h-3.5" />
                  Learned
                </div>
                <p className="text-3xl font-semibold text-[#C2E94B] tabular-nums">
                  {completados}
                </p>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Section header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-white">Your cases</h2>
            <p className="text-sm text-zinc-500 mt-1">
              {loading
                ? "Loading…"
                : `${casos.length} ${casos.length === 1 ? "case" : "cases"} in the knowledge base`}
            </p>
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex items-center gap-3 text-zinc-500 text-sm">
              <div className="relative">
                <div className="w-8 h-8 border-2 border-[#C2E94B]/20 rounded-full" />
                <div className="absolute inset-0 w-8 h-8 border-2 border-[#C2E94B] border-t-transparent rounded-full animate-spin" />
              </div>
              Loading cases...
            </div>
          </div>
        ) : error ? (
          <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-10 text-center">
            <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto mb-3" />
            <p className="text-zinc-300 mb-5">{error}</p>
            <Button
              onClick={loadCasos}
              variant="outline"
              className="border-zinc-700 bg-transparent text-zinc-300 hover:text-white hover:border-zinc-600"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        ) : casos.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-zinc-800 bg-[#0d0d0d] p-16 text-center">
            <div className="w-16 h-16 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mx-auto mb-5">
              <FileText className="w-8 h-8 text-zinc-600" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">
              No cases yet
            </h3>
            <p className="text-zinc-500 mb-6 max-w-sm mx-auto">
              Create your first case so the multi-agent system can start
              building its forensic memory.
            </p>
            <Link href="/casos/nuevo">
              <Button className="bg-[#C2E94B] text-[#0a0a0a] hover:bg-[#d4f06d] font-medium">
                <Plus className="w-4 h-4 mr-2" />
                Create first case
              </Button>
            </Link>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {casos.map((caso, idx) => {
              const cfg = estadoConfig(caso.estado);
              return (
                <motion.div
                  key={caso.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25, delay: Math.min(idx * 0.03, 0.3) }}
                >
                  <Link href={`/casos/${caso.id}`} className="group block h-full">
                    <div className="h-full rounded-2xl border border-zinc-800/60 bg-[#111] p-5 transition-all duration-200 hover:border-[#C2E94B]/40 hover:bg-[#141414]">
                      <div className="flex items-center justify-between mb-4">
                        <span className="text-xs font-medium text-zinc-300 bg-zinc-800/60 px-2.5 py-1 rounded-full">
                          {tipoLabel(caso.tipo_colision)}
                        </span>
                        <span
                          className={`inline-flex items-center gap-1.5 text-xs font-medium ${cfg.text}`}
                        >
                          <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
                          {cfg.label}
                        </span>
                      </div>

                      <h3 className="text-base font-semibold text-white truncate mb-1">
                        Case #{caso.id}
                      </h3>
                      <p className="text-sm text-zinc-500">
                        {new Date(caso.fecha_accidente).toLocaleDateString(
                          "en-US",
                          { dateStyle: "long" },
                        )}
                      </p>

                      <div className="mt-4 pt-4 border-t border-zinc-800/60 flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-xs text-zinc-500">
                          <MapPin className="w-3.5 h-3.5" />
                          <span className="tabular-nums">
                            {caso.ubicacion.lat.toFixed(3)},{" "}
                            {caso.ubicacion.lon.toFixed(3)}
                          </span>
                        </div>
                        <ArrowRight className="w-4 h-4 text-zinc-600 group-hover:text-[#C2E94B] group-hover:translate-x-0.5 transition-all" />
                      </div>
                    </div>
                  </Link>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
