"use client";

import { useRef } from "react";
import Link from "next/link";
import { motion, useInView } from "framer-motion";
import {
  ArrowRight,
  FileSearch,
  Scale,
  Shield,
  Zap,
  Brain,
  Eye,
  CheckCircle2,
  Sparkles,
  Car,
  FileText,
  Gavel,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

// React Bits Components
import {
  GradientText,
  BlurText,
  CountUp,
  Particles,
  SpotlightCard,
  Magnet,
} from "@/components/reactbits";

// Variantes de animacion
const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 },
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const scaleIn = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { opacity: 1, scale: 1 },
};

export default function Home() {
  const featuresRef = useRef(null);
  const casesRef = useRef(null);
  const pipelineRef = useRef(null);

  const featuresInView = useInView(featuresRef, { once: true, margin: "-100px" });
  const casesInView = useInView(casesRef, { once: true, margin: "-100px" });
  const pipelineInView = useInView(pipelineRef, { once: true, margin: "-100px" });

  return (
    <main className="min-h-screen bg-veridict-green-900 overflow-hidden">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center">
        {/* Particles Background */}
        <Particles
          quantity={80}
          staticity={30}
          ease={80}
          color="#C2E94B"
          particleSize={3}
        />

        {/* Gradient overlays */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(194,233,75,0.12)_0%,_transparent_60%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_rgba(42,68,53,0.8)_0%,_transparent_50%)]" />

        {/* Grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: `linear-gradient(rgba(194,233,75,0.5) 1px, transparent 1px),
                             linear-gradient(90deg, rgba(194,233,75,0.5) 1px, transparent 1px)`,
            backgroundSize: "80px 80px",
          }}
        />

        <div className="container relative z-10 mx-auto px-6 py-20">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={staggerContainer}
            className="max-w-5xl mx-auto text-center"
          >
            {/* Badge */}
            <motion.div variants={fadeInUp} className="mb-8">
              <span className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-veridict-lime/10 border border-veridict-lime/30 text-veridict-lime text-sm font-medium backdrop-blur-sm">
                <Sparkles className="w-4 h-4" />
                Powered by Multi-Agent AI
              </span>
            </motion.div>

            {/* Title with Gradient Text */}
            <motion.h1
              variants={fadeInUp}
              className="text-6xl md:text-8xl font-bold tracking-tight mb-6"
            >
              <GradientText
                colors={["#C2E94B", "#60efff", "#C2E94B", "#60efff"]}
                animationSpeed={6}
                className="inline-block"
              >
                Veridict
              </GradientText>{" "}
              <span className="text-veridict-white">AI</span>
            </motion.h1>

            {/* Subtitle with BlurText */}
            <motion.div variants={fadeInUp} className="mb-12">
              <BlurText
                text="Reconstruccion forense automatizada de accidentes de trafico. Dictamenes periciales en formato UNE-EN 16775 con calculos fisicos justificados."
                delay={0.03}
                className="text-xl md:text-2xl text-veridict-gray max-w-3xl mx-auto leading-relaxed"
                animateBy="words"
                direction="top"
              />
            </motion.div>

            {/* CTA Buttons with Magnet Effect */}
            <motion.div
              variants={fadeInUp}
              className="flex flex-col sm:flex-row gap-4 justify-center mb-20"
            >
              <Magnet magnetStrength={3} padding={50}>
                <Link href="/demo">
                  <Button size="lg" className="group text-lg px-8 py-6">
                    Ver Demo en Vivo
                    <ArrowRight className="w-5 h-5 ml-2 transition-transform group-hover:translate-x-1" />
                  </Button>
                </Link>
              </Magnet>
              <Magnet magnetStrength={3} padding={50}>
                <Link href="/casos/nuevo">
                  <Button variant="outline" size="lg" className="text-lg px-8 py-6">
                    Nuevo Caso
                  </Button>
                </Link>
              </Magnet>
            </motion.div>

            {/* Stats with CountUp */}
            <motion.div
              variants={fadeInUp}
              className="grid grid-cols-3 gap-8 max-w-2xl mx-auto pt-12 border-t border-white/10"
            >
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-veridict-lime">
                  <CountUp to={5} duration={2} className="tabular-nums" />
                </div>
                <div className="text-sm text-veridict-gray mt-2">Agentes IA</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-veridict-lime">
                  <CountUp to={100} duration={2.5} className="tabular-nums" />%
                </div>
                <div className="text-sm text-veridict-gray mt-2">Trazable</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-veridict-lime">
                  UNE
                </div>
                <div className="text-sm text-veridict-gray mt-2">Certificado</div>
              </div>
            </motion.div>
          </motion.div>

          {/* Scroll indicator */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 2, duration: 0.5 }}
            className="absolute bottom-8 left-1/2 -translate-x-1/2"
          >
            <motion.div
              animate={{ y: [0, 8, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="w-6 h-10 rounded-full border-2 border-veridict-lime/30 flex items-start justify-center p-2"
            >
              <motion.div className="w-1.5 h-1.5 rounded-full bg-veridict-lime" />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Pipeline Section */}
      <section ref={pipelineRef} className="py-32 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-veridict-green-800/50 to-transparent" />

        <div className="container relative z-10 mx-auto px-6">
          <motion.div
            initial="hidden"
            animate={pipelineInView ? "visible" : "hidden"}
            variants={staggerContainer}
            className="text-center mb-20"
          >
            <motion.div variants={fadeInUp}>
              <GradientText
                colors={["#C2E94B", "#ffffff", "#C2E94B"]}
                animationSpeed={8}
                className="text-4xl md:text-5xl font-bold"
              >
                Sistema Multi-Agente
              </GradientText>
            </motion.div>
            <motion.p
              variants={fadeInUp}
              className="text-veridict-gray max-w-2xl mx-auto mt-6 text-lg"
            >
              Cinco agentes de IA especializados trabajan en colaboracion para analizar,
              reconstruir y verificar cada caso con precision forense.
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            animate={pipelineInView ? "visible" : "hidden"}
            variants={staggerContainer}
            className="grid md:grid-cols-5 gap-4"
          >
            {[
              { icon: Eye, name: "Intake", desc: "OCR y vision AI", color: "#60efff" },
              { icon: Car, name: "Reconstructor", desc: "Fisica del impacto", color: "#C2E94B" },
              { icon: FileText, name: "Analyst", desc: "Sintesis de datos", color: "#feca57" },
              { icon: Gavel, name: "Legal", desc: "Marco normativo", color: "#ff6b6b" },
              { icon: Shield, name: "Verifier", desc: "Devil's Advocate", color: "#a55eea" },
            ].map((agent, i) => (
              <motion.div key={agent.name} variants={scaleIn}>
                <SpotlightCard
                  spotlightColor={`${agent.color}20`}
                  className="rounded-xl"
                >
                  <Card className="relative p-6 text-center border-veridict-green-600 hover:border-veridict-lime/40 transition-all duration-500 h-full">
                    {i < 4 && (
                      <div className="hidden md:block absolute -right-3 top-1/2 -translate-y-1/2 z-10">
                        <motion.div
                          animate={{ x: [0, 4, 0] }}
                          transition={{ duration: 1.5, repeat: Infinity }}
                        >
                          <ArrowRight className="w-5 h-5 text-veridict-lime/50" />
                        </motion.div>
                      </div>
                    )}
                    <div
                      className="w-14 h-14 mx-auto mb-4 rounded-xl flex items-center justify-center transition-all duration-300"
                      style={{ backgroundColor: `${agent.color}15` }}
                    >
                      <agent.icon className="w-7 h-7" style={{ color: agent.color }} />
                    </div>
                    <h3 className="font-bold text-veridict-white text-lg mb-1">{agent.name}</h3>
                    <p className="text-sm text-veridict-gray">{agent.desc}</p>
                  </Card>
                </SpotlightCard>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section ref={featuresRef} className="py-32">
        <div className="container mx-auto px-6">
          <motion.div
            initial="hidden"
            animate={featuresInView ? "visible" : "hidden"}
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp} className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-veridict-white mb-4">
                Capacidades Avanzadas
              </h2>
              <p className="text-veridict-gray max-w-xl mx-auto">
                Tecnologia de vanguardia para reconstruccion forense de accidentes
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <FeatureCard
                icon={<FileSearch className="w-7 h-7" />}
                title="Analisis Multi-Fuente"
                description="OCR de atestados, analisis de fotos con vision AI, datos AEMET y DGT integrados"
                color="#60efff"
              />
              <FeatureCard
                icon={<Zap className="w-7 h-7" />}
                title="Calculos CRASH3"
                description="Velocidad por deformacion, Stannard Baker, conservacion de momento lineal"
                color="#C2E94B"
              />
              <FeatureCard
                icon={<Scale className="w-7 h-7" />}
                title="Razonamiento Legal"
                description="RAG sobre corpus legal espanol con citas verificadas del BOE y jurisprudencia"
                color="#feca57"
              />
              <FeatureCard
                icon={<Shield className="w-7 h-7" />}
                title="Verificacion Adversarial"
                description="Devil's Advocate valida coherencia fisica y compatibilidad de versiones"
                color="#a55eea"
              />
            </div>
          </motion.div>
        </div>
      </section>

      {/* Demo Cases */}
      <section ref={casesRef} className="py-32 relative">
        <div className="absolute inset-0 bg-gradient-to-t from-veridict-green-800/30 to-transparent" />

        <div className="container relative z-10 mx-auto px-6">
          <motion.div
            initial="hidden"
            animate={casesInView ? "visible" : "hidden"}
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp} className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-veridict-white mb-4">
                Casos de Demostracion
              </h2>
              <p className="text-veridict-gray max-w-xl mx-auto">
                Explora reconstrucciones completas de accidentes reales procesados por nuestro sistema
              </p>
            </motion.div>

            <motion.div variants={staggerContainer} className="grid md:grid-cols-3 gap-6">
              <CasePreview
                id="1"
                title="Cambio de carril M-30"
                type="Alcance lateral"
                description="Lluvia, exceso velocidad, cambio sin senalizar"
                status="completed"
              />
              <CasePreview
                id="2"
                title="Atropello C/ Alcala"
                type="Atropello peaton"
                description="Version conductor incompatible con fisica"
                status="completed"
              />
              <CasePreview
                id="3"
                title="Colision multiple A-6"
                type="Alcance trasero"
                description="Sin huellas frenada (ABS), datos EDR disponibles"
                status="completed"
              />
            </motion.div>

            <motion.div variants={fadeInUp} className="text-center mt-12">
              <Magnet magnetStrength={2} padding={40}>
                <Link href="/casos">
                  <Button variant="outline" size="lg" className="text-lg px-8">
                    Ver todos los casos
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </Link>
              </Magnet>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-32 relative">
        <Particles
          quantity={40}
          staticity={50}
          ease={100}
          color="#C2E94B"
          particleSize={2}
        />

        <div className="container relative z-10 mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="max-w-3xl mx-auto text-center"
          >
            <motion.div
              animate={{
                scale: [1, 1.05, 1],
                rotate: [0, 5, -5, 0]
              }}
              transition={{ duration: 4, repeat: Infinity }}
              className="inline-block mb-8"
            >
              <Brain className="w-20 h-20 text-veridict-lime" />
            </motion.div>

            <h2 className="text-4xl md:text-5xl font-bold text-veridict-white mb-6">
              <GradientText
                colors={["#C2E94B", "#60efff", "#C2E94B"]}
                animationSpeed={5}
              >
                Dictamenes periciales
              </GradientText>
              <br />
              con precision de IA
            </h2>

            <p className="text-xl text-veridict-gray mb-10">
              Reduce el tiempo de elaboracion de informes periciales de dias a minutos,
              manteniendo el rigor tecnico y la trazabilidad completa.
            </p>

            <Magnet magnetStrength={2} padding={60}>
              <Link href="/casos/nuevo">
                <Button size="lg" className="group text-lg px-10 py-6">
                  Comenzar ahora
                  <ArrowRight className="w-5 h-5 ml-2 transition-transform group-hover:translate-x-2" />
                </Button>
              </Link>
            </Magnet>
          </motion.div>
        </div>
      </section>
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  description,
  color,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
}) {
  return (
    <motion.div variants={fadeInUp}>
      <SpotlightCard spotlightColor={`${color}15`} className="rounded-xl h-full">
        <Card className="p-6 h-full border-veridict-green-600 hover:border-veridict-lime/30 transition-all duration-300">
          <div
            className="w-14 h-14 rounded-xl flex items-center justify-center mb-5"
            style={{ backgroundColor: `${color}15` }}
          >
            <div style={{ color }}>{icon}</div>
          </div>
          <h3 className="font-bold text-veridict-white text-lg mb-2">{title}</h3>
          <p className="text-sm text-veridict-gray leading-relaxed">{description}</p>
        </Card>
      </SpotlightCard>
    </motion.div>
  );
}

function CasePreview({
  id,
  title,
  type,
  description,
  status,
}: {
  id: string;
  title: string;
  type: string;
  description: string;
  status: "completed" | "processing" | "pending";
}) {
  return (
    <motion.div variants={scaleIn}>
      <Link href={`/casos/${id}`}>
        <SpotlightCard spotlightColor="rgba(194, 233, 75, 0.1)" className="rounded-xl">
          <Card className="p-6 h-full border-veridict-green-600 hover:border-veridict-lime/40 transition-all duration-300 cursor-pointer group">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-semibold text-veridict-lime bg-veridict-lime/10 px-3 py-1.5 rounded-full">
                {type}
              </span>
              {status === "completed" && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  <CheckCircle2 className="w-5 h-5 text-veridict-lime" />
                </motion.div>
              )}
            </div>
            <h3 className="font-bold text-veridict-white text-lg mb-2 group-hover:text-veridict-lime transition-colors">
              {title}
            </h3>
            <p className="text-sm text-veridict-gray">{description}</p>
          </Card>
        </SpotlightCard>
      </Link>
    </motion.div>
  );
}
