"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Play, FileSearch, Bot, Shield, Lock, LayoutDashboard, Clock, Target, Zap, ArrowRight } from "lucide-react";

export default function Home() {
  return (
    <main className="bg-white min-h-screen">
      {/* HERO - Full Viewport Video */}
      <section className="relative h-screen w-full overflow-hidden">
        {/* Video Background */}
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover"
        >
          <source src="/hero-video.mp4" type="video/mp4" />
        </video>

        {/* Overlay gradient */}
        <div className="absolute inset-0 bg-black/50" />

        {/* Nav */}
        <nav className="absolute top-0 left-0 right-0 z-20 flex items-center justify-between p-6 md:px-12 md:py-8">
          <Link href="/">
            <img
              src="/logo.png"
              alt="Veridict"
              className="h-10 md:h-12 w-auto"
            />
          </Link>

          <div className="flex items-center gap-3">
            <Link href="/casos">
              <button className="flex items-center gap-2 px-5 py-2.5 border border-white/30 text-white font-medium rounded-full hover:bg-white/10 transition-colors">
                <LayoutDashboard className="w-4 h-4" />
                Dashboard
              </button>
            </Link>
            <Link href="/casos">
              <button className="px-5 py-2.5 bg-[#C2E94B] text-[#1a1a1a] font-medium rounded-full hover:bg-[#d4f06d] transition-colors">
                View Demo
              </button>
            </Link>
          </div>
        </nav>

        {/* Hero Content */}
        <div className="relative z-10 h-full flex items-center justify-center px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-4xl"
          >
            <p className="text-[#C2E94B] text-sm font-medium tracking-wide uppercase mb-6">
              AI-Powered Forensic Reconstruction
            </p>

            <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold text-white leading-[1.1] mb-8">
              AI-powered
              <br />
              <span className="text-[#C2E94B]">forensic crash analysis</span>
            </h1>

            <p className="text-lg md:text-xl text-white/70 max-w-lg mx-auto mb-10">
              AI that analyzes accidents and generates court-ready forensic reports.
            </p>

            <div className="flex items-center justify-center gap-4">
              <Link href="/casos">
                <button className="flex items-center gap-2 px-8 py-4 bg-[#C2E94B] text-[#1a1a1a] font-semibold rounded-full hover:bg-[#d4f06d] transition-colors">
                  <Play className="w-5 h-5 fill-current" />
                  View Demo
                </button>
              </Link>
            </div>
          </motion.div>
        </div>

        {/* Scroll hint */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10"
        >
          <motion.div
            animate={{ y: [0, 6, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="w-6 h-10 rounded-full border-2 border-white/30 flex justify-center pt-2"
          >
            <div className="w-1.5 h-1.5 rounded-full bg-white/50" />
          </motion.div>
        </motion.div>
      </section>

      {/* FEATURES - White section with image */}
      <section className="py-24 md:py-32 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-16 text-center"
          >
            <p className="text-[#1a1a1a]/40 text-sm font-medium tracking-wide uppercase mb-4">
              How it works
            </p>
            <h2 className="text-4xl md:text-6xl font-bold text-[#1a1a1a] leading-tight mb-6">
              From 3 days of work
              <br />
              <span className="text-[#C2E94B]">to 2 minutes.</span>
            </h2>
            <p className="text-lg text-[#666] max-w-2xl mx-auto">
              Our AI pipeline automates the entire forensic reconstruction process
            </p>
          </motion.div>

          {/* Two column layout: Image left, Features right */}
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: Image */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="flex justify-center"
            >
              <img
                src="/laptop-docs.jpg"
                alt="AI generating forensic reports"
                className="w-full max-w-md lg:max-w-lg object-contain"
              />
            </motion.div>

            {/* Right: Feature cards in vertical stack */}
            <div className="flex flex-col gap-5">
              {[
                {
                  num: "01",
                  icon: FileSearch,
                  title: "Atestado + evidence ingestion",
                  desc: "Parses Guardia Civil atestados, photos and witness statements, and pulls real-time meteo, OSM road data and sun position for the scene.",
                },
                {
                  num: "02",
                  icon: Bot,
                  title: "7-agent forensic pipeline",
                  desc: "Forensic Analyst (CRASH3/SB physics), Legal Reasoner (RGC/LSV), Declaration Analyst, Adjudicator (Opus), Devil's Advocate and Report Writer — running in parallel phases.",
                },
                {
                  num: "03",
                  icon: Shield,
                  title: "UNE-EN 16775",
                  desc: "Court-ready peritajes following European forensic standards, with adversarial verification before sign-off.",
                },
                {
                  num: "04",
                  icon: Lock,
                  title: "Sigstore signature",
                  desc: "Each PDF is hashed and signed via Sigstore for cryptographic proof of authenticity and chain of custody.",
                },
              ].map((item, i) => (
                <motion.div
                  key={item.num}
                  initial={{ opacity: 0, x: 30 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="group p-6 rounded-2xl bg-[#f5f5f5] hover:bg-[#1a1a1a] transition-all duration-300"
                >
                  <div className="flex items-center gap-5">
                    <div className="flex-shrink-0 w-14 h-14 rounded-xl bg-[#1a1a1a] group-hover:bg-[#C2E94B] flex items-center justify-center transition-colors">
                      <item.icon className="w-7 h-7 text-[#C2E94B] group-hover:text-[#1a1a1a] transition-colors" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <span className="text-xs font-mono text-[#1a1a1a]/40 group-hover:text-white/40 transition-colors">
                          {item.num}
                        </span>
                        <h3 className="text-lg font-semibold text-[#1a1a1a] group-hover:text-white transition-colors">
                          {item.title}
                        </h3>
                      </div>
                      <p className="text-[#666] group-hover:text-white/60 text-sm leading-relaxed transition-colors">
                        {item.desc}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA - Screenshot based */}
      <section className="relative py-24 md:py-32 bg-[#0a0a0a]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-5 gap-12 items-center">
            {/* Left: CTA (2 cols) */}
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="lg:col-span-2"
            >
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Try the demo
              </h2>
              <p className="text-white/50 mb-6">
                Real case. Real analysis. See the full report.
              </p>
              <Link href="/casos">
                <button className="flex items-center gap-2 px-6 py-3 bg-[#C2E94B] text-[#0a0a0a] font-semibold rounded-full hover:bg-[#d4f06d] transition-colors">
                  <span>Open Demo</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </Link>
            </motion.div>

            {/* Right: App mockup (3 cols) */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="lg:col-span-3"
            >
              <div className="relative rounded-xl overflow-hidden border border-white/10 bg-[#111] shadow-2xl">
                {/* Window header */}
                <div className="flex items-center gap-2 px-4 py-3 border-b border-white/10 bg-[#0a0a0a]">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-[#ff5f57]" />
                    <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
                    <div className="w-3 h-3 rounded-full bg-[#28ca41]" />
                  </div>
                  <div className="flex-1 text-center">
                    <span className="text-xs text-white/30 font-mono">veridict.app/casos/demo-1</span>
                  </div>
                </div>

                {/* App content mockup */}
                <div className="p-4 space-y-3">
                  {/* Header row */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg bg-[#C2E94B]/20 flex items-center justify-center">
                        <FileSearch className="w-4 h-4 text-[#C2E94B]" />
                      </div>
                      <div>
                        <div className="text-sm text-white font-medium">Aulestia Case</div>
                        <div className="text-xs text-white/40">Pedestrian collision · A Coruña</div>
                      </div>
                    </div>
                    <div className="px-2 py-1 rounded bg-[#C2E94B]/10 text-[#C2E94B] text-xs font-medium">
                      Completed
                    </div>
                  </div>

                  {/* Tabs mockup */}
                  <div className="flex gap-1 border-b border-white/10 pb-2">
                    {["Report", "Simulation", "Reasoning"].map((tab, i) => (
                      <div
                        key={tab}
                        className={`px-3 py-1.5 text-xs rounded-md ${i === 0 ? "bg-white/10 text-white" : "text-white/40"}`}
                      >
                        {tab}
                      </div>
                    ))}
                  </div>

                  {/* Report content mockup */}
                  <div className="grid grid-cols-3 gap-3">
                    {/* Left panel - questions */}
                    <div className="col-span-2 space-y-2">
                      <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                        <div className="text-xs text-[#C2E94B] mb-1 font-mono">C1</div>
                        <div className="text-xs text-white/70 mb-2">Vehicle speed at impact</div>
                        <div className="h-1 w-3/4 bg-white/10 rounded" />
                        <div className="h-1 w-1/2 bg-white/10 rounded mt-1" />
                      </div>
                      <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                        <div className="text-xs text-[#C2E94B] mb-1 font-mono">C2</div>
                        <div className="text-xs text-white/70 mb-2">Collision avoidability</div>
                        <div className="h-1 w-full bg-white/10 rounded" />
                        <div className="h-1 w-2/3 bg-white/10 rounded mt-1" />
                      </div>
                    </div>

                    {/* Right panel - data */}
                    <div className="space-y-2">
                      <div className="p-2 rounded-lg bg-[#C2E94B]/5 border border-[#C2E94B]/20">
                        <div className="text-[10px] text-white/40 mb-1">Speed</div>
                        <div className="text-lg text-white font-bold">52 <span className="text-xs text-white/50">km/h</span></div>
                      </div>
                      <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                        <div className="text-[10px] text-white/40 mb-1">Energy</div>
                        <div className="text-lg text-white font-bold">48 <span className="text-xs text-white/50">kJ</span></div>
                      </div>
                      <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                        <div className="text-[10px] text-white/40 mb-1">Confidence</div>
                        <div className="text-lg text-[#C2E94B] font-bold">94%</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Gradient fade */}
                <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-[#0a0a0a] to-transparent pointer-events-none" />
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-[#1a1a1a] pt-16 pb-8">
        <div className="max-w-6xl mx-auto px-6">
          {/* Top section */}
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-10 pb-12 border-b border-white/10">
            {/* Brand */}
            <div className="flex flex-col gap-4">
              <Link href="/">
                <img
                  src="/logo.png"
                  alt="Veridict"
                  className="h-10 w-auto"
                />
              </Link>
              <p className="text-white/40 text-sm max-w-xs">
                AI-powered forensic reconstruction for traffic accidents.
              </p>
            </div>

            {/* Links */}
            <div className="flex gap-16">
              <div>
                <h4 className="text-white font-medium mb-4">Product</h4>
                <ul className="space-y-3">
                  <li>
                    <Link href="/casos/1" className="text-white/50 hover:text-[#C2E94B] transition-colors text-sm">
                      Demo
                    </Link>
                  </li>
                </ul>
              </div>
              <div>
                <h4 className="text-white font-medium mb-4">Legal</h4>
                <ul className="space-y-3">
                  <li>
                    <span className="text-white/50 text-sm">Privacy</span>
                  </li>
                  <li>
                    <span className="text-white/50 text-sm">Terms</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* Bottom section */}
          <div className="pt-8">
            <p className="text-white/30 text-sm">
              © 2026 Veridict. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </main>
  );
}
