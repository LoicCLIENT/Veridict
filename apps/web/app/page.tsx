"use client";

import Link from "next/link";
import { ArrowRight, FileSearch, Scale, Shield, Zap } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-secondary/20">
      {/* Hero */}
      <section className="container mx-auto px-4 py-24 text-center">
        <h1 className="text-5xl font-bold tracking-tight mb-6">
          <span className="text-primary">Veridict</span>{" "}
          <span className="text-muted-foreground">AI</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
          Reconstruccion forense automatizada de accidentes de trafico.
          Dictamenes periciales en formato UNE-EN 16775 con calculos fisicos
          justificados y verificacion adversarial.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/casos"
            className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-lg font-medium hover:opacity-90 transition"
          >
            Ver casos demo
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/casos/nuevo"
            className="inline-flex items-center gap-2 border border-border px-6 py-3 rounded-lg font-medium hover:bg-secondary transition"
          >
            Nuevo caso
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <FeatureCard
            icon={<FileSearch className="w-8 h-8" />}
            title="Analisis Multi-Fuente"
            description="OCR de atestados, analisis de fotos con vision AI, datos AEMET y DGT"
          />
          <FeatureCard
            icon={<Zap className="w-8 h-8" />}
            title="Calculos CRASH3"
            description="Velocidad por deformacion, Stannard Baker, conservacion de momento"
          />
          <FeatureCard
            icon={<Scale className="w-8 h-8" />}
            title="Razonamiento Legal"
            description="RAG sobre corpus legal espanol con citas verificadas del BOE"
          />
          <FeatureCard
            icon={<Shield className="w-8 h-8" />}
            title="Verificacion Adversarial"
            description="Devil's Advocate valida coherencia fisica y compatibilidad de versiones"
          />
        </div>
      </section>

      {/* Demo Cases Preview */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Casos Demo</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <CasePreview
            id="1"
            title="Cambio de carril M-30"
            type="Alcance lateral"
            description="Lluvia, exceso velocidad, cambio sin senalizar"
          />
          <CasePreview
            id="2"
            title="Atropello Alcala"
            type="Atropello peaton"
            description="Version conductor incompatible con fisica"
          />
          <CasePreview
            id="3"
            title="Alcance A-6"
            type="Alcance trasero"
            description="Sin huellas frenada (ABS), datos EDR"
          />
        </div>
      </section>
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="p-6 rounded-xl border border-border bg-card">
      <div className="text-primary mb-4">{icon}</div>
      <h3 className="font-semibold mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  );
}

function CasePreview({
  id,
  title,
  type,
  description,
}: {
  id: string;
  title: string;
  type: string;
  description: string;
}) {
  return (
    <Link href={`/casos/${id}`}>
      <div className="p-6 rounded-xl border border-border bg-card hover:border-primary/50 transition cursor-pointer">
        <span className="text-xs font-medium text-primary bg-primary/10 px-2 py-1 rounded">
          {type}
        </span>
        <h3 className="font-semibold mt-3 mb-2">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
    </Link>
  );
}
