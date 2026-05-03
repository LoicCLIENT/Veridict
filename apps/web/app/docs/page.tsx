"use client";

import { motion } from "framer-motion";
import {
  FileText,
  Car,
  Scale,
  Shield,
  Database,
  Cloud,
  Cpu,
  Lock,
  CheckCircle2,
  ArrowRight,
  Code,
  Zap,
  Eye,
  BookOpen,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const agents = [
  {
    id: "extractor",
    name: "Extractor Agent",
    icon: FileText,
    color: "blue",
    description: "Processes documents and case evidence",
    capabilities: [
      "OCR of police reports (scanned PDFs)",
      "Photo analysis with Vision AI",
      "Data extraction from accident report forms",
      "Automatic queries to AEMET and DGT",
      "Location geocoding",
    ],
    tech: ["Claude Vision", "Tesseract OCR", "External APIs"],
  },
  {
    id: "reconstructor",
    name: "Reconstructor Agent",
    icon: Car,
    color: "purple",
    description: "Calculates accident physics",
    capabilities: [
      "Pre-braking speed (Stannard-Baker)",
      "EBS from deformation (CRASH3/NHTSA)",
      "Linear momentum conservation",
      "Skid mark analysis",
      "Trajectory reconstruction",
    ],
    tech: ["Physical models", "CRASH3", "EDR Data"],
  },
  {
    id: "legal",
    name: "Legal Agent",
    icon: Scale,
    color: "amber",
    description: "Analyzes violations and applicable regulations",
    capabilities: [
      "RAG over Spanish legal corpus",
      "RGC violation detection",
      "Verified BOE citations",
      "Relevant case law",
      "Liability attribution",
    ],
    tech: ["RAG", "Embeddings", "Vector DB"],
  },
  {
    id: "adversarial",
    name: "Devil's Advocate",
    icon: Shield,
    color: "red",
    description: "Verifies coherence and detects contradictions",
    capabilities: [
      "Physical coherence verification",
      "Version comparison vs evidence",
      "Contradiction detection",
      "Plausibility analysis",
      "Human review escalation if needed",
    ],
    tech: ["Adversarial verification", "Logic checks"],
  },
];

const techStack = [
  { name: "Claude AI", category: "LLM", icon: Cpu },
  { name: "Next.js 15", category: "Frontend", icon: Code },
  { name: "FastAPI", category: "Backend", icon: Zap },
  { name: "Supabase", category: "Database", icon: Database },
  { name: "Sigstore", category: "Audit", icon: Lock },
  { name: "Vercel", category: "Deploy", icon: Cloud },
];

const compliance = [
  {
    name: "UNE-EN 16775",
    description: "European standard for private investigation services",
    status: "Compliant",
  },
  {
    name: "GDPR",
    description: "General Data Protection Regulation",
    status: "Compliant",
  },
  {
    name: "ISO 27001",
    description: "Information security management system",
    status: "In progress",
  },
];

function AgentDiagram() {
  return (
    <div className="relative py-12">
      {/* Pipeline visual */}
      <div className="flex items-center justify-between max-w-4xl mx-auto">
        {agents.map((agent, idx) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="flex items-center"
          >
            {/* Agent */}
            <div className="relative">
              <motion.div
                className={`w-20 h-20 rounded-2xl flex items-center justify-center
                  ${agent.color === "blue" ? "bg-blue-500/20 border-blue-500/40" : ""}
                  ${agent.color === "purple" ? "bg-purple-500/20 border-purple-500/40" : ""}
                  ${agent.color === "amber" ? "bg-amber-500/20 border-amber-500/40" : ""}
                  ${agent.color === "red" ? "bg-red-500/20 border-red-500/40" : ""}
                  border-2
                `}
                whileHover={{ scale: 1.05 }}
              >
                <agent.icon
                  className={`w-8 h-8
                    ${agent.color === "blue" ? "text-blue-400" : ""}
                    ${agent.color === "purple" ? "text-purple-400" : ""}
                    ${agent.color === "amber" ? "text-amber-400" : ""}
                    ${agent.color === "red" ? "text-red-400" : ""}
                  `}
                />
              </motion.div>
              <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 whitespace-nowrap">
                <span className="text-xs font-medium text-veridict-white">{agent.name.split(" ")[1]}</span>
              </div>
            </div>

            {/* Arrow */}
            {idx < agents.length - 1 && (
              <motion.div
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ delay: idx * 0.1 + 0.3 }}
                className="w-12 h-0.5 bg-gradient-to-r from-veridict-lime/50 to-veridict-lime mx-2"
              />
            )}
          </motion.div>
        ))}
      </div>

      {/* Input and Output */}
      <div className="flex justify-between max-w-5xl mx-auto mt-16 text-sm">
        <div className="flex items-center gap-2 text-veridict-gray">
          <FileText className="w-4 h-4" />
          <span>Police Report + Photos</span>
        </div>
        <div className="flex items-center gap-2 text-veridict-lime">
          <span>UNE-EN 16775 Expert Report</span>
          <CheckCircle2 className="w-4 h-4" />
        </div>
      </div>
    </div>
  );
}

export default function DocsPage() {
  return (
    <div className="min-h-screen py-12">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <Badge className="mb-4 bg-veridict-lime/20 text-veridict-lime border-veridict-lime/40">
            <BookOpen className="w-3 h-3 mr-1" />
            Technical Documentation
          </Badge>
          <h1 className="text-4xl font-bold text-veridict-white mb-4">
            Veridict AI Architecture
          </h1>
          <p className="text-veridict-gray max-w-2xl mx-auto">
            Automated forensic reconstruction system based on 4 specialized AI agents
            working in a sequential pipeline.
          </p>
        </motion.div>

        {/* Pipeline Diagram */}
        <Card className="p-8 mb-12">
          <h2 className="text-xl font-semibold text-veridict-white mb-2 text-center">
            Processing Pipeline
          </h2>
          <p className="text-veridict-gray text-center text-sm mb-8">
            From police report to expert verdict in less than 10 minutes
          </p>
          <AgentDiagram />
        </Card>

        {/* Agents in detail */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-veridict-white mb-6 text-center">
            The 4 Agents
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {agents.map((agent, idx) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <Card className="p-6 h-full">
                  <div className="flex items-start gap-4 mb-4">
                    <div
                      className={`p-3 rounded-xl
                        ${agent.color === "blue" ? "bg-blue-500/20 text-blue-400" : ""}
                        ${agent.color === "purple" ? "bg-purple-500/20 text-purple-400" : ""}
                        ${agent.color === "amber" ? "bg-amber-500/20 text-amber-400" : ""}
                        ${agent.color === "red" ? "bg-red-500/20 text-red-400" : ""}
                      `}
                    >
                      <agent.icon className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-veridict-white">{agent.name}</h3>
                      <p className="text-sm text-veridict-gray">{agent.description}</p>
                    </div>
                  </div>

                  <div className="mb-4">
                    <h4 className="text-xs font-medium text-veridict-gray mb-2">CAPABILITIES:</h4>
                    <ul className="space-y-1">
                      {agent.capabilities.map((cap, i) => (
                        <li key={i} className="text-sm text-veridict-white flex items-start gap-2">
                          <CheckCircle2 className="w-3 h-3 text-veridict-lime mt-1 flex-shrink-0" />
                          {cap}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {agent.tech.map((t, i) => (
                      <Badge key={i} variant="outline" className="text-xs">
                        {t}
                      </Badge>
                    ))}
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-veridict-white mb-6 text-center">
            Tech Stack
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {techStack.map((tech, idx) => (
              <motion.div
                key={tech.name}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.05 }}
              >
                <Card className="p-4 text-center hover:border-veridict-lime/40 transition-colors">
                  <tech.icon className="w-8 h-8 mx-auto mb-2 text-veridict-lime" />
                  <div className="font-medium text-veridict-white text-sm">{tech.name}</div>
                  <div className="text-xs text-veridict-gray">{tech.category}</div>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Compliance */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-veridict-white mb-6 text-center">
            Regulatory Compliance
          </h2>
          <div className="grid md:grid-cols-3 gap-4">
            {compliance.map((item, idx) => (
              <motion.div
                key={item.name}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <Card className="p-6">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-veridict-white">{item.name}</h3>
                    <Badge
                      className={
                        item.status === "Compliant"
                          ? "bg-veridict-lime/20 text-veridict-lime border-veridict-lime/40"
                          : "bg-amber-500/20 text-amber-400 border-amber-500/40"
                      }
                    >
                      {item.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-veridict-gray">{item.description}</p>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Physics Formulas */}
        <Card className="p-8 mb-12">
          <h2 className="text-2xl font-bold text-veridict-white mb-6 text-center">
            Physics Calculations Used
          </h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="font-semibold text-veridict-white mb-3">
                Pre-Braking Speed (Stannard-Baker)
              </h3>
              <div className="bg-veridict-green-800 rounded-lg p-4 font-mono text-center mb-3">
                <span className="text-veridict-lime text-xl">V = √(2 × μ × g × d)</span>
              </div>
              <ul className="text-sm text-veridict-gray space-y-1">
                <li>• V = Initial speed (m/s)</li>
                <li>• μ = Friction coefficient</li>
                <li>• g = Gravity (9.81 m/s²)</li>
                <li>• d = Braking distance (m)</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-veridict-white mb-3">
                EBS from Deformation (CRASH3)
              </h3>
              <div className="bg-veridict-green-800 rounded-lg p-4 font-mono text-center mb-3">
                <span className="text-veridict-lime text-xl">EBS = √((A×C + B×C²/2) / m)</span>
              </div>
              <ul className="text-sm text-veridict-gray space-y-1">
                <li>• EBS = Equivalent Barrier Speed</li>
                <li>• A, B = NHTSA stiffness coefficients</li>
                <li>• C = Deformation depth</li>
                <li>• m = Vehicle mass</li>
              </ul>
            </div>
          </div>
        </Card>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center"
        >
          <Card className="p-8 bg-gradient-to-br from-veridict-lime/10 to-transparent border-veridict-lime/30">
            <Eye className="w-12 h-12 text-veridict-lime mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-veridict-white mb-2">
              Want to see it in action?
            </h3>
            <p className="text-veridict-gray mb-6">
              Try the interactive demo with a real case processed by the 4 agents.
            </p>
            <a
              href="/demo"
              className="inline-flex items-center gap-2 px-6 py-3 bg-veridict-lime text-veridict-green-900 rounded-lg font-medium hover:bg-veridict-lime/90 transition-colors"
            >
              View Demo
              <ArrowRight className="w-4 h-4" />
            </a>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
