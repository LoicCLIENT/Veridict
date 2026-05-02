"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Shield,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  User,
  Car,
  Zap,
  Scale,
  Eye,
  FileText,
  ArrowRight,
  Sparkles,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface VersionData {
  conductor: string;
  vehiculo: string;
  declaracion: string;
  afirmaciones: {
    id: string;
    texto: string;
    compatible: boolean | null; // null = pendiente de verificar
    evidencia?: string;
    contradiccion?: string;
  }[];
}

interface EvidenciaFisica {
  id: string;
  tipo: "huella" | "deformacion" | "testigo" | "camara" | "clima";
  titulo: string;
  valor: string;
  unidad?: string;
  implicacion: string;
}

interface ConfrontacionTabProps {
  versionA?: VersionData;
  versionB?: VersionData;
  evidencias?: EvidenciaFisica[];
  veredictoFinal?: {
    versionACompatible: boolean;
    versionBCompatible: boolean;
    contradiccionesA: number;
    contradiccionesB: number;
    resumen: string;
  };
}

// Datos de ejemplo dramáticos
const mockVersionA: VersionData = {
  conductor: "Juan García López",
  vehiculo: "Vehículo A - Seat León",
  declaracion:
    "Circulaba por el carril derecho respetando el límite de velocidad cuando el otro vehículo invadió mi carril sin previo aviso.",
  afirmaciones: [
    {
      id: "a1",
      texto: "Circulaba a 50 km/h (dentro del límite)",
      compatible: false,
      evidencia: "Huella de frenada: 12.5m",
      contradiccion: "La física indica V₀ = 67.3 km/h (17 km/h por encima del límite)",
    },
    {
      id: "a2",
      texto: "El otro vehículo cambió de carril sin señalizar",
      compatible: true,
      evidencia: "Testigo presencial confirma ausencia de intermitente",
    },
    {
      id: "a3",
      texto: "Frené inmediatamente al detectar el peligro",
      compatible: true,
      evidencia: "Huella continua de 12.5m consistente con frenada de emergencia",
    },
    {
      id: "a4",
      texto: "No tuve tiempo de evitar la colisión",
      compatible: true,
      evidencia: "Tiempo de reacción de 0.8s dentro de parámetros normales",
    },
  ],
};

const mockVersionB: VersionData = {
  conductor: "María Rodríguez Sanz",
  vehiculo: "Vehículo B - Volkswagen Golf",
  declaracion:
    "Señalicé correctamente el cambio de carril y el otro vehículo venía a velocidad excesiva y no me dio tiempo a completar la maniobra.",
  afirmaciones: [
    {
      id: "b1",
      texto: "Señalicé con el intermitente antes de cambiar",
      compatible: false,
      evidencia: "Testigo presencial y grabación de cámara",
      contradiccion: "No se observa activación del intermitente en ningún momento",
    },
    {
      id: "b2",
      texto: "Verifiqué el retrovisor antes de la maniobra",
      compatible: false,
      evidencia: "Posición de impacto y velocidad relativa",
      contradiccion: "El vehículo A era visible en el espejo 3 segundos antes del impacto",
    },
    {
      id: "b3",
      texto: "El vehículo A venía muy rápido",
      compatible: true,
      evidencia: "Velocidad calculada: 67.3 km/h (17 km/h sobre límite)",
    },
    {
      id: "b4",
      texto: "Circulaba a 55 km/h",
      compatible: true,
      evidencia: "Compatible con daños observados y conservación de momento",
    },
  ],
};

const mockEvidencias: EvidenciaFisica[] = [
  {
    id: "e1",
    tipo: "huella",
    titulo: "Huella de frenada",
    valor: "12.5",
    unidad: "metros",
    implicacion: "Indica V₀ = 67.3 km/h aplicando Stannard-Baker con μ=0.65",
  },
  {
    id: "e2",
    tipo: "deformacion",
    titulo: "Deformación vehículo A",
    valor: "23",
    unidad: "cm",
    implicacion: "EBS = 45.2 km/h según modelo CRASH3",
  },
  {
    id: "e3",
    tipo: "testigo",
    titulo: "Declaración testigo",
    valor: "Sr. López Martín",
    implicacion: "Confirma que vehículo B no señalizó el cambio de carril",
  },
  {
    id: "e4",
    tipo: "clima",
    titulo: "Condiciones meteorológicas",
    valor: "Lluvia ligera",
    implicacion: "Coeficiente de fricción reducido (μ=0.65)",
  },
];

const mockVeredicto = {
  versionACompatible: false,
  versionBCompatible: false,
  contradiccionesA: 1,
  contradiccionesB: 2,
  resumen:
    "Ambas versiones contienen afirmaciones incompatibles con la evidencia física. Sin embargo, el vehículo B presenta más contradicciones críticas relacionadas con la ejecución de la maniobra.",
};

export default function ConfrontacionTab({
  versionA = mockVersionA,
  versionB = mockVersionB,
  evidencias = mockEvidencias,
  veredictoFinal = mockVeredicto,
}: ConfrontacionTabProps) {
  const [showingPhase, setShowingPhase] = useState(0);
  const [revealedItems, setRevealedItems] = useState<Set<string>>(new Set());
  const [analysisComplete, setAnalysisComplete] = useState(false);

  // Animación secuencial dramática
  useEffect(() => {
    const phases = [
      // Fase 0: Mostrar versiones
      () => setShowingPhase(1),
      // Fase 1: Revelar evidencias
      () => setShowingPhase(2),
      // Fase 2: Comenzar análisis
      () => {
        // Revelar afirmaciones una por una
        const allIds = [
          ...versionA.afirmaciones.map((a) => a.id),
          ...versionB.afirmaciones.map((a) => a.id),
        ];
        allIds.forEach((id, idx) => {
          setTimeout(() => {
            setRevealedItems((prev) => new Set([...prev, id]));
          }, idx * 400);
        });
        setTimeout(() => {
          setShowingPhase(3);
          setAnalysisComplete(true);
        }, allIds.length * 400 + 500);
      },
    ];

    const timers: NodeJS.Timeout[] = [];
    phases.forEach((phase, idx) => {
      timers.push(setTimeout(phase, idx * 800));
    });

    return () => timers.forEach(clearTimeout);
  }, [versionA.afirmaciones, versionB.afirmaciones]);

  const renderAfirmacion = (
    afirmacion: VersionData["afirmaciones"][0],
    vehiculo: "A" | "B"
  ) => {
    const isRevealed = revealedItems.has(afirmacion.id);
    const colorClass = vehiculo === "A" ? "blue" : "orange";

    return (
      <motion.div
        key={afirmacion.id}
        initial={{ opacity: 0, x: vehiculo === "A" ? -20 : 20 }}
        animate={{
          opacity: isRevealed ? 1 : 0.3,
          x: 0,
        }}
        transition={{ duration: 0.3 }}
        className={`
          p-3 rounded-lg border transition-all duration-300
          ${!isRevealed ? "border-veridict-green-700 bg-veridict-green-800/50" : ""}
          ${isRevealed && afirmacion.compatible === true ? "border-veridict-lime/50 bg-veridict-lime/10" : ""}
          ${isRevealed && afirmacion.compatible === false ? "border-veridict-error/50 bg-veridict-error/10" : ""}
          ${isRevealed && afirmacion.compatible === null ? "border-veridict-gray/50 bg-veridict-gray/10" : ""}
        `}
      >
        <div className="flex items-start gap-2">
          <AnimatePresence mode="wait">
            {isRevealed ? (
              afirmacion.compatible === true ? (
                <motion.div
                  key="check"
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  className="mt-0.5"
                >
                  <CheckCircle2 className="w-4 h-4 text-veridict-lime flex-shrink-0" />
                </motion.div>
              ) : afirmacion.compatible === false ? (
                <motion.div
                  key="x"
                  initial={{ scale: 0, rotate: 180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  className="mt-0.5"
                >
                  <XCircle className="w-4 h-4 text-veridict-error flex-shrink-0" />
                </motion.div>
              ) : (
                <motion.div key="pending" className="mt-0.5">
                  <div className="w-4 h-4 rounded-full border-2 border-veridict-gray flex-shrink-0" />
                </motion.div>
              )
            ) : (
              <motion.div
                key="loading"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="mt-0.5"
              >
                <div className="w-4 h-4 border-2 border-veridict-lime/30 border-t-veridict-lime rounded-full flex-shrink-0" />
              </motion.div>
            )}
          </AnimatePresence>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-veridict-white">&quot;{afirmacion.texto}&quot;</p>
            {isRevealed && afirmacion.evidencia && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                transition={{ delay: 0.2 }}
                className="mt-2"
              >
                <div className="text-xs text-veridict-gray flex items-center gap-1">
                  <FileText className="w-3 h-3" />
                  {afirmacion.evidencia}
                </div>
                {afirmacion.contradiccion && (
                  <motion.div
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="mt-1 p-2 rounded bg-veridict-error/20 border border-veridict-error/30"
                  >
                    <div className="flex items-start gap-1">
                      <AlertTriangle className="w-3 h-3 text-veridict-error mt-0.5 flex-shrink-0" />
                      <span className="text-xs text-veridict-error">
                        {afirmacion.contradiccion}
                      </span>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            )}
          </div>
        </div>
      </motion.div>
    );
  };

  const contradiccionesA = versionA.afirmaciones.filter((a) => a.compatible === false).length;
  const contradiccionesB = versionB.afirmaciones.filter((a) => a.compatible === false).length;

  return (
    <div className="p-6 h-full overflow-y-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-veridict-error/10 border border-veridict-error/30 mb-4">
          <Shield className="w-5 h-5 text-veridict-error" />
          <span className="text-sm font-medium text-veridict-error">
            Devil&apos;s Advocate Analysis
          </span>
        </div>
        <h2 className="text-2xl font-bold text-veridict-white mb-2">
          Confrontación de Versiones
        </h2>
        <p className="text-veridict-gray max-w-xl mx-auto">
          Análisis adversarial comparando las declaraciones de ambos conductores
          contra la evidencia física objetiva
        </p>
      </motion.div>

      {/* Grid principal: Version A | Evidencias | Version B */}
      <div className="grid lg:grid-cols-3 gap-6 mb-8">
        {/* Versión A */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: showingPhase >= 1 ? 1 : 0, x: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-4"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-blue-500/20 border border-blue-500/40 flex items-center justify-center">
              <Car className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h3 className="font-semibold text-veridict-white">Vehículo A</h3>
              <p className="text-xs text-veridict-gray">{versionA.conductor}</p>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/20 mb-4">
            <div className="flex items-start gap-2 mb-2">
              <User className="w-4 h-4 text-blue-400 mt-0.5" />
              <span className="text-xs font-medium text-blue-400">DECLARACIÓN</span>
            </div>
            <p className="text-sm text-veridict-white italic">
              &quot;{versionA.declaracion}&quot;
            </p>
          </div>

          <div className="space-y-2">
            <div className="text-xs font-medium text-veridict-gray mb-2 flex items-center gap-2">
              <Eye className="w-3 h-3" />
              AFIRMACIONES VERIFICADAS
            </div>
            {versionA.afirmaciones.map((a) => renderAfirmacion(a, "A"))}
          </div>

          {/* Resumen versión A */}
          <AnimatePresence>
            {analysisComplete && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`p-4 rounded-lg border ${
                  contradiccionesA > 0
                    ? "bg-veridict-error/10 border-veridict-error/30"
                    : "bg-veridict-lime/10 border-veridict-lime/30"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-veridict-white">
                    Credibilidad
                  </span>
                  <Badge
                    className={
                      contradiccionesA > 0
                        ? "bg-veridict-error/20 text-veridict-error border-veridict-error/40"
                        : "bg-veridict-lime/20 text-veridict-lime border-veridict-lime/40"
                    }
                  >
                    {contradiccionesA} contradicción{contradiccionesA !== 1 ? "es" : ""}
                  </Badge>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Evidencias Físicas - Centro */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: showingPhase >= 2 ? 1 : 0, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-4"
        >
          <div className="text-center mb-4">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-veridict-lime/10 border border-veridict-lime/30">
              <Zap className="w-4 h-4 text-veridict-lime" />
              <span className="text-xs font-medium text-veridict-lime">
                EVIDENCIA OBJETIVA
              </span>
            </div>
          </div>

          <div className="space-y-3">
            {evidencias.map((evidencia, idx) => (
              <motion.div
                key={evidencia.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.15 }}
                className="p-4 rounded-lg bg-veridict-green-800 border border-veridict-green-600 hover:border-veridict-lime/40 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`p-2 rounded-lg ${
                      evidencia.tipo === "huella"
                        ? "bg-purple-500/20 text-purple-400"
                        : evidencia.tipo === "deformacion"
                        ? "bg-orange-500/20 text-orange-400"
                        : evidencia.tipo === "testigo"
                        ? "bg-blue-500/20 text-blue-400"
                        : evidencia.tipo === "camara"
                        ? "bg-cyan-500/20 text-cyan-400"
                        : "bg-yellow-500/20 text-yellow-400"
                    }`}
                  >
                    {evidencia.tipo === "huella" && <Car className="w-4 h-4" />}
                    {evidencia.tipo === "deformacion" && <Zap className="w-4 h-4" />}
                    {evidencia.tipo === "testigo" && <User className="w-4 h-4" />}
                    {evidencia.tipo === "camara" && <Eye className="w-4 h-4" />}
                    {evidencia.tipo === "clima" && <Sparkles className="w-4 h-4" />}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium text-veridict-gray">
                        {evidencia.titulo}
                      </span>
                    </div>
                    <div className="text-lg font-mono text-veridict-lime">
                      {evidencia.valor}
                      {evidencia.unidad && (
                        <span className="text-sm text-veridict-gray ml-1">
                          {evidencia.unidad}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-veridict-gray mt-1">
                      {evidencia.implicacion}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Versión B */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: showingPhase >= 1 ? 1 : 0, x: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-4"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-orange-500/20 border border-orange-500/40 flex items-center justify-center">
              <Car className="w-6 h-6 text-orange-400" />
            </div>
            <div>
              <h3 className="font-semibold text-veridict-white">Vehículo B</h3>
              <p className="text-xs text-veridict-gray">{versionB.conductor}</p>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-orange-500/5 border border-orange-500/20 mb-4">
            <div className="flex items-start gap-2 mb-2">
              <User className="w-4 h-4 text-orange-400 mt-0.5" />
              <span className="text-xs font-medium text-orange-400">DECLARACIÓN</span>
            </div>
            <p className="text-sm text-veridict-white italic">
              &quot;{versionB.declaracion}&quot;
            </p>
          </div>

          <div className="space-y-2">
            <div className="text-xs font-medium text-veridict-gray mb-2 flex items-center gap-2">
              <Eye className="w-3 h-3" />
              AFIRMACIONES VERIFICADAS
            </div>
            {versionB.afirmaciones.map((a) => renderAfirmacion(a, "B"))}
          </div>

          {/* Resumen versión B */}
          <AnimatePresence>
            {analysisComplete && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`p-4 rounded-lg border ${
                  contradiccionesB > 0
                    ? "bg-veridict-error/10 border-veridict-error/30"
                    : "bg-veridict-lime/10 border-veridict-lime/30"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-veridict-white">
                    Credibilidad
                  </span>
                  <Badge
                    className={
                      contradiccionesB > 0
                        ? "bg-veridict-error/20 text-veridict-error border-veridict-error/40"
                        : "bg-veridict-lime/20 text-veridict-lime border-veridict-lime/40"
                    }
                  >
                    {contradiccionesB} contradicción{contradiccionesB !== 1 ? "es" : ""}
                  </Badge>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>

      {/* Veredicto Final */}
      <AnimatePresence>
        {analysisComplete && (
          <motion.div
            initial={{ opacity: 0, y: 30, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.5, type: "spring" }}
            className="mt-8"
          >
            <div className="p-6 rounded-2xl bg-gradient-to-br from-veridict-error/10 via-veridict-green-800 to-veridict-lime/10 border border-veridict-green-600 relative overflow-hidden">
              {/* Decorative elements */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-veridict-error/10 blur-3xl" />
              <div className="absolute bottom-0 left-0 w-32 h-32 bg-veridict-lime/10 blur-3xl" />

              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-3 rounded-xl bg-veridict-error/20 border border-veridict-error/40">
                    <Scale className="w-6 h-6 text-veridict-error" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-veridict-white">
                      Conclusión del Análisis Adversarial
                    </h3>
                    <p className="text-xs text-veridict-gray">
                      Verificación automática por Devil&apos;s Advocate
                    </p>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  {/* Resultado Versión A */}
                  <div
                    className={`p-4 rounded-xl border ${
                      veredictoFinal.versionACompatible
                        ? "bg-veridict-lime/10 border-veridict-lime/30"
                        : "bg-veridict-error/10 border-veridict-error/30"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-medium text-blue-400">Versión A</span>
                      {veredictoFinal.versionACompatible ? (
                        <Badge className="bg-veridict-lime/20 text-veridict-lime">
                          <CheckCircle2 className="w-3 h-3 mr-1" />
                          Compatible
                        </Badge>
                      ) : (
                        <Badge className="bg-veridict-error/20 text-veridict-error">
                          <XCircle className="w-3 h-3 mr-1" />
                          Contradicciones
                        </Badge>
                      )}
                    </div>
                    <div className="text-3xl font-bold text-veridict-white">
                      {veredictoFinal.contradiccionesA}
                      <span className="text-sm font-normal text-veridict-gray ml-2">
                        afirmaciones falsas
                      </span>
                    </div>
                  </div>

                  {/* Resultado Versión B */}
                  <div
                    className={`p-4 rounded-xl border ${
                      veredictoFinal.versionBCompatible
                        ? "bg-veridict-lime/10 border-veridict-lime/30"
                        : "bg-veridict-error/10 border-veridict-error/30"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-medium text-orange-400">Versión B</span>
                      {veredictoFinal.versionBCompatible ? (
                        <Badge className="bg-veridict-lime/20 text-veridict-lime">
                          <CheckCircle2 className="w-3 h-3 mr-1" />
                          Compatible
                        </Badge>
                      ) : (
                        <Badge className="bg-veridict-error/20 text-veridict-error">
                          <XCircle className="w-3 h-3 mr-1" />
                          Contradicciones
                        </Badge>
                      )}
                    </div>
                    <div className="text-3xl font-bold text-veridict-white">
                      {veredictoFinal.contradiccionesB}
                      <span className="text-sm font-normal text-veridict-gray ml-2">
                        afirmaciones falsas
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-4 rounded-lg bg-veridict-green-900/50 border border-veridict-green-700">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <div className="text-sm font-medium text-amber-400 mb-1">
                        Análisis Imparcial
                      </div>
                      <p className="text-sm text-veridict-white">
                        {veredictoFinal.resumen}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
