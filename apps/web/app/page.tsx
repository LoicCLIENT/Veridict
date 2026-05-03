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
            <Link href="/casos/demo-1">
              <button className="flex items-center gap-2 px-5 py-2.5 border border-white/30 text-white font-medium rounded-full hover:bg-white/10 transition-colors">
                <LayoutDashboard className="w-4 h-4" />
                Dashboard
              </button>
            </Link>
            <Link href="/casos/demo-1">
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
              Expert reports
              <br />
              <span className="text-[#C2E94B]">in minutes</span>
            </h1>

            <p className="text-lg md:text-xl text-white/70 max-w-lg mx-auto mb-10">
              AI that analyzes accidents and generates court-ready forensic reports.
            </p>

            <div className="flex items-center justify-center gap-4">
              <Link href="/casos/demo-1">
                <button className="flex items-center gap-2 px-8 py-4 bg-[#C2E94B] text-[#1a1a1a] font-semibold rounded-full hover:bg-[#d4f06d] transition-colors">
                  <Play className="w-5 h-5 fill-current" />
                  View Demo
                </button>
              </Link>
              <Link href="/docs">
                <button className="px-8 py-4 text-white font-medium hover:text-[#C2E94B] transition-colors">
                  Documentation
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
                  title: "Automated analysis",
                  desc: "Processes police reports, photos, and EDR data automatically with AI vision.",
                },
                {
                  num: "02",
                  icon: Bot,
                  title: "5 AI agents",
                  desc: "Multi-agent pipeline that cross-validates every finding for accuracy.",
                },
                {
                  num: "03",
                  icon: Shield,
                  title: "UNE-EN 16775",
                  desc: "Court-ready reports following European forensic standards.",
                },
                {
                  num: "04",
                  icon: Lock,
                  title: "Sigstore signature",
                  desc: "Cryptographic proof of authenticity and chain of custody.",
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

      {/* CTA - Revolut/Vercel Style */}
      <section className="relative py-32 md:py-40 bg-[#0a0a0a] overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0">
          {/* Gradient orbs */}
          <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[#C2E94B]/10 rounded-full blur-[120px]" />
          <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-[#C2E94B]/5 rounded-full blur-[100px]" />
          {/* Grid pattern */}
          <div
            className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
              backgroundSize: '60px 60px'
            }}
          />
        </div>

        <div className="relative max-w-6xl mx-auto px-6">
          {/* Stats Row */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="grid grid-cols-3 gap-8 mb-20"
          >
            {[
              { value: "2", unit: "min", label: "Average report time", icon: Clock },
              { value: "95", unit: "%", label: "Accuracy rate", icon: Target },
              { value: "10", unit: "x", label: "Faster than manual", icon: Zap },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 + 0.2 }}
                className="text-center group"
              >
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-white/5 mb-4 group-hover:bg-[#C2E94B]/10 transition-colors">
                  <stat.icon className="w-6 h-6 text-[#C2E94B]" />
                </div>
                <div className="flex items-baseline justify-center gap-1 mb-2">
                  <span className="text-5xl md:text-6xl font-bold text-white">{stat.value}</span>
                  <span className="text-2xl md:text-3xl font-semibold text-[#C2E94B]">{stat.unit}</span>
                </div>
                <p className="text-sm text-white/40">{stat.label}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* Main CTA */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="text-center"
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8"
            >
              <span className="w-2 h-2 rounded-full bg-[#C2E94B] animate-pulse" />
              <span className="text-sm text-white/60">Ready to transform your workflow</span>
            </motion.div>

            <h2 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
              Start analyzing
              <br />
              <span className="bg-gradient-to-r from-[#C2E94B] via-[#d4f06d] to-[#C2E94B] bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient">
                in seconds
              </span>
            </h2>

            <p className="text-lg md:text-xl text-white/40 max-w-xl mx-auto mb-12">
              Upload your case files and let our AI agents handle the rest.
              Court-ready reports, delivered instantly.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/casos/demo-1">
                <motion.button
                  whileHover={{ scale: 1.02, boxShadow: "0 0 40px rgba(194, 233, 75, 0.3)" }}
                  whileTap={{ scale: 0.98 }}
                  className="group flex items-center gap-3 px-8 py-4 bg-[#C2E94B] text-[#0a0a0a] font-semibold rounded-full transition-all duration-300"
                >
                  <span>Open Demo</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </motion.button>
              </Link>
              <Link href="/casos/demo-1">
                <motion.button
                  whileHover={{ scale: 1.02, backgroundColor: "rgba(255,255,255,0.1)" }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center gap-2 px-8 py-4 text-white font-medium rounded-full border border-white/20 transition-all duration-300"
                >
                  <LayoutDashboard className="w-5 h-5" />
                  <span>View Dashboard</span>
                </motion.button>
              </Link>
            </div>
          </motion.div>

          {/* Bottom decoration */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.6 }}
            className="flex items-center justify-center gap-8 mt-20 text-white/20 text-sm"
          >
            <span className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              UNE-EN 16775
            </span>
            <span className="w-1 h-1 rounded-full bg-white/20" />
            <span className="flex items-center gap-2">
              <Lock className="w-4 h-4" />
              Sigstore Signed
            </span>
            <span className="w-1 h-1 rounded-full bg-white/20" />
            <span className="flex items-center gap-2">
              <Bot className="w-4 h-4" />
              5 AI Agents
            </span>
          </motion.div>
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
                  <li>
                    <Link href="/docs" className="text-white/50 hover:text-[#C2E94B] transition-colors text-sm">
                      Documentation
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
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pt-8">
            <p className="text-white/30 text-sm">
              © 2025 Veridict. All rights reserved.
            </p>
            <div className="flex items-center gap-2">
              <span className="text-white/30 text-sm">Made with</span>
              <span className="text-[#C2E94B]">♥</span>
              <span className="text-white/30 text-sm">for forensic experts</span>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
