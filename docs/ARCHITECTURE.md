# Veridict AI - Architecture

## Overview

Veridict AI is a multi-agent system for automated forensic reconstruction of traffic accidents. It uses a pipeline of specialized AI agents to analyze evidence, perform physics calculations, reason about legal implications, and generate professional reports.

## System Architecture

```
                    +-----------------+
                    |   Frontend      |
                    |   (Next.js)     |
                    +--------+--------+
                             |
                             v
                    +--------+--------+
                    |   Backend API   |
                    |   (FastAPI)     |
                    +--------+--------+
                             |
        +--------------------+--------------------+
        |                    |                    |
        v                    v                    v
+-------+-------+   +--------+-------+   +--------+-------+
| External APIs |   | Vector DB      |   | Storage        |
| (AEMET, OSM)  |   | (Qdrant)       |   | (Supabase/R2)  |
+---------------+   +----------------+   +----------------+
```

## Multi-Agent Pipeline

```
[Input Data] -> [Auto-Extract] -> [Forensic Analyst] -> [Legal Reasoner]
                                         |                    |
                                         v                    v
                                  [Adjudicator] ---------> [Devil's Advocate]
                                         |                    |
                                         v                    v
                                  [Report Writer] <----- [Pass/Fail]
                                         |
                                         v
                                  [PDF + Sigstore]
```

### Agent Responsibilities

1. **Forensic Analyst** (Claude Opus)
   - CRASH3 deformation analysis
   - Stannard Baker brake mark analysis
   - Momentum conservation verification
   - Timeline reconstruction

2. **Legal Reasoner** (GPT-4o + RAG)
   - Spanish traffic law corpus search
   - Infraction identification
   - Jurisprudence matching
   - Article citation

3. **Adjudicator** (Claude Opus)
   - Fault attribution calculation
   - Version compatibility analysis
   - Confidence scoring

4. **Devil's Advocate** (Claude Opus)
   - Physics coherence verification
   - Version plausibility check
   - Biomechanical validation
   - Adversarial challenge

5. **Report Writer** (Claude Opus)
   - UNE-EN 16775 format generation
   - PDF creation
   - Sigstore signing

## Data Flow

1. **Input**: Atestado PDF, photos, measurements
2. **Extraction**: OCR + Vision AI analysis
3. **Context**: Weather, road, sun position
4. **Analysis**: Physics + Legal reasoning
5. **Verification**: Adversarial review
6. **Output**: Signed PDF report

## Technology Stack

### Frontend
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui
- Mapbox GL JS
- Zustand state management

### Backend
- Python 3.11
- FastAPI + uvicorn
- Pydantic v2
- LangGraph orchestration
- NumPy/SciPy physics

### AI/ML
- Claude Opus 4.5 (Anthropic)
- GPT-4o (OpenAI)
- text-embedding-3-large
- Qdrant vector search

### Infrastructure
- Vercel (frontend)
- Railway/Render (backend)
- Supabase (database)
- Cloudflare R2 (storage)
- Sigstore (audit trail)
