# Veridict

> AI-powered forensic reconstruction of traffic accidents.
> Nexforge Hackathon 2026 · Open Track

---

## TL;DR

Multi-agent system that receives accident data (police reports, photos, expert measurements) and returns a forensic report in UNE-EN 16775 format with justified physics calculations (CRASH3, Stannard Baker), Spanish legal citations, and adversarial verification — all in under 90 seconds.

**Demo output:** Web app deployed on Vercel with pre-loaded cases. Click a case → processes live → shows complete report with animated map, timeline, calculations, legal reasoning, and downloadable PDF.

🔗 **Live Demo:** https://veridict-two.vercel.app

---

## Quick Setup

### Requirements
- Node.js 20+
- Python 3.11+
- pnpm (`npm install -g pnpm`)
- Docker (optional, for local Qdrant)
- Git

### Required Accounts

- [ ] Anthropic API → https://console.anthropic.com (Claude Opus 4 credits)
- [ ] OpenAI API → https://platform.openai.com (GPT-4o + embeddings)
- [ ] Mapbox → https://account.mapbox.com (free tier 50k req/month)
- [ ] AEMET OpenData → https://opendata.aemet.es/centrodedescargas/altaUsuario
- [ ] Qdrant Cloud → https://cloud.qdrant.io (free tier 1GB)
- [ ] Supabase → https://supabase.com (free tier sufficient)
- [ ] Vercel → https://vercel.com (frontend deploy)
- [ ] Cloudflare → https://dash.cloudflare.com (R2 for storage)

### Clone and Run

```bash
git clone git@github.com:LoicCLIENT/Veridict.git
cd Veridict

# Environment variables
cp .env.example .env

# Frontend
cd apps/web
pnpm install
pnpm dev          # http://localhost:3000

# Backend (separate terminal)
cd apps/api
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn main:app --reload     # http://localhost:8000

# Local Vector DB (optional, if not using Qdrant Cloud)
docker run -p 6333:6333 qdrant/qdrant
```

---

## Tech Stack

### Frontend
- **Next.js 15** (App Router + Turbopack)
- **TypeScript** strict
- **Tailwind CSS** + **shadcn/ui**
- **Mapbox GL JS** for reconstruction map
- **Recharts** for physics graphs
- **Framer Motion** for timeline slider and animations
- **react-pdf** for PDF generation
- **Zustand** for global state

### Backend
- **Python 3.11**
- **FastAPI** + **uvicorn**
- **Pydantic v2** validation
- **NumPy + SciPy + filterpy** physics processing
- **Anthropic SDK** multi-agent orchestration
- **Pint** physical units
- **Tesseract** OCR for police reports
- **Pillow** image processing

### LLMs and Data
- **Claude Opus 4** (Anthropic) → main reasoning
- **Claude Sonnet 4** (Anthropic) → specialized agents
- **GPT-4o** (OpenAI) → cross-verification
- **Claude Vision** → qualitative photo analysis
- **OpenAI text-embedding-3-large** → legal embeddings
- **Qdrant** → vector DB

### Infrastructure
- **Vercel** → frontend
- **Railway or Render** → FastAPI backend
- **Supabase** → PostgreSQL + Auth + Storage
- **Cloudflare R2** → heavy files (PDFs, photos)
- **Sigstore** → cryptographic audit trail

---

## Environment Variables

`.env.example`:

```bash
# LLMs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Public Data
AEMET_API_KEY=eyJhbGc...
MAPBOX_ACCESS_TOKEN=pk.eyJ...

# Storage
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET=veridict-uploads

# Vector DB
QDRANT_URL=https://xxx.cloud.qdrant.io
QDRANT_API_KEY=...
QDRANT_COLLECTION=corpus_trafico_es

# Backend
DATABASE_URL=postgresql://...
API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Sigstore (optional, uses public OIDC)
SIGSTORE_REKOR_URL=https://rekor.sigstore.dev
```

---

## Repository Structure

```
Veridict/
├── apps/
│   ├── web/                    # Next.js frontend
│   │   ├── app/
│   │   │   ├── page.tsx              # Landing
│   │   │   ├── casos/
│   │   │   │   ├── nuevo/page.tsx    # New case form
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx      # Final report
│   │   │   │       └── procesando/page.tsx
│   │   │   └── pipeline/page.tsx     # Educational mockup
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn
│   │   │   ├── MapaReconstruccion.tsx
│   │   │   ├── CronologiaTimeline.tsx
│   │   │   ├── CalculosFisicos.tsx
│   │   │   ├── RazonamientoLegal.tsx
│   │   │   └── DictamenPDF.tsx
│   │   └── lib/
│   │       ├── api.ts                # API client
│   │       └── store.ts              # Zustand
│   │
│   └── api/                    # FastAPI backend
│       ├── main.py                   # entrypoint
│       ├── routers/
│       │   ├── casos.py
│       │   ├── upload.py
│       │   ├── analisis.py
│       │   └── dictamen.py
│       ├── agents/
│       │   ├── orchestrator.py       # Multi-agent orchestration
│       │   ├── specialists/
│       │   │   ├── perito.py         # Forensic Analyst
│       │   │   ├── legal.py          # Legal Reasoner
│       │   │   ├── adjudicator.py
│       │   │   ├── devils_advocate.py
│       │   │   └── report_writer.py
│       ├── physics/
│       │   ├── crash3.py             # EBS by deformation
│       │   ├── stannard_baker.py     # Pre-braking speed
│       │   ├── momentum.py           # Momentum conservation
│       │   ├── kalman.py             # Sensor fusion filters
│       │   ├── biomechanics.py       # Delta-V, AIS, Prasad-Mertz
│       │   └── coefficients.py       # NHTSA A/B table
│       ├── extract/
│       │   ├── atestado_ocr.py       # Police report PDF OCR
│       │   ├── parte_amistoso.py     # OCR + parser
│       │   └── vision.py             # Claude Vision for photos
│       ├── data/
│       │   ├── aemet.py              # AEMET client
│       │   ├── dgt.py                # DGT data
│       │   ├── osm.py                # OpenStreetMap Overpass
│       │   └── suncalc.py            # Solar position
│       ├── rag/
│       │   ├── ingest.py             # Load corpus to Qdrant
│       │   ├── retrieve.py           # Search with filters
│       │   └── corpus/               # Downloaded BOE PDFs
│       ├── reports/
│       │   ├── pdf_generator.py      # PDF UNE-EN 16775 format
│       │   └── templates/
│       └── audit/
│           └── sigstore_signer.py    # Cryptographic signature
│
├── packages/
│   ├── types/                  # Shared TypeScript types
│   └── physics-validators/     # Client+server validations
│
├── data/
│   ├── casos_demo/             # PRE-LOADED DEMO CASES
│   │   ├── caso_1_madrid_m30/
│   │   │   ├── atestado.pdf
│   │   │   ├── parte_amistoso.pdf
│   │   │   ├── fotos/
│   │   │   ├── mediciones.json
│   │   │   └── ground_truth.json    # Real expert report
│   │   ├── caso_2_atropello_alcala/
│   │   └── caso_3_alcance_a6/
│   └── corpus_legal/           # BOE PDFs
│
├── scripts/
│   ├── ingest_corpus.py        # Load legal corpus to Qdrant
│   ├── seed_demo_casos.py      # Pre-load demo cases in DB
│   └── grabar_demo.sh          # OBS automation
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEMO_SCRIPT.md          # Pitch script
│   └── QA_PREP.md              # 10 jury questions
│
├── .env.example
├── pnpm-workspace.yaml
└── README.md
```

---

## API Endpoints

Base URL: `http://localhost:8000` (dev)

### Cases

```
POST   /api/casos                          # Create case
GET    /api/casos                          # List cases
GET    /api/casos/{id}                     # Case details
DELETE /api/casos/{id}                     # Delete
```

### Upload

```
POST   /api/casos/{id}/upload/atestado     # Upload police report PDF → OCR
POST   /api/casos/{id}/upload/parte        # Upload friendly report → OCR
POST   /api/casos/{id}/upload/foto         # Upload photo → Claude Vision
POST   /api/casos/{id}/mediciones          # Manual expert measurements
```

### Analysis

```
POST   /api/casos/{id}/analizar            # Launch multi-agent pipeline (async)
GET    /api/casos/{id}/estado              # Poll progress
GET    /api/casos/{id}/dictamen            # Complete report when ready
GET    /api/casos/{id}/pdf                 # Download PDF UNE-EN 16775 format
GET    /api/casos/{id}/audit               # Sigstore audit trail
```

### Public Data (cached)

```
GET    /api/data/meteo?lat=&lon=&t=        # AEMET
GET    /api/data/via?lat=&lon=             # DGT + OSM
GET    /api/data/sol?lat=&lon=&t=          # SunCalc
GET    /api/data/vehiculo?modelo=          # A/B coefficients
```

### Demo

```
GET    /api/demo/casos                     # List 2-3 pre-loaded cases
POST   /api/demo/casos/{id}/reset          # Reset state for new demo
```

---

## Multi-Agent Pipeline

```
[Complete case data]
        ↓
[Auto-extract] ─── AEMET, DGT, OSM, SunCalc in parallel
        ↓
[Forensic Analyst] ─── uses Claude Opus 4
   └→ Calculates: CRASH3, Stannard Baker, momentum
   └→ Returns structured JSON timeline
        ↓
[Legal Reasoner] ─── uses Claude Sonnet 4 + RAG Qdrant
   └→ Searches applicable RGC/LSV articles
   └→ Retrieves CENDOJ jurisprudence
   └→ Returns infractions with citations
        ↓
[Adjudicator] ─── uses Claude Opus 4
   └→ Calculates % fault
   └→ Assigns confidence score
        ↓
   ┌────┴────┐
   │ ≥ 0.85  │ < 0.85
   ↓         ↓
[Devil's    [Escalate
 Advocate]   to human]
   ↓
   ├─ verify momentum conservation
   ├─ verify EBS vs braking marks coherence
   ├─ verify statement compatibility
   └─ verify biomechanical coherence
   ↓
   ┌────┴────┐
   │ passes  │ refutes
   ↓         ↓
[Report    [Escalate
 Writer]    to human]
   ↓
[PDF UNE-EN 16775]
   ↓
[Sigstore Signature]
```

---

## Demo Cases

Each case = directory in `data/casos_demo/` with:

- `atestado.pdf` (real or realistic synthetic)
- `parte_amistoso.pdf` optional
- `fotos/` with location and damage photos
- `mediciones.json` with expert measurements (C1-C6, braking length, etc.)
- `ground_truth.json` with real expert report (for comparison)

### Case 1 — Lane change without signaling M-30
- Type: lateral rear-end
- Driver A traveling 67 km/h in 50 zone, rain
- Driver B changes lane without signaling
- Expected result: 65% fault A, 35% fault B

### Case 2 — Pedestrian crossing collision (Aulestia)
- Type: pedestrian collision
- Driver at 52 km/h in 30 zone according to deformations
- Driver claims 30 km/h
- Expected result: driver version INCOMPATIBLE with physics
- **Demo highlight piece**

### Case 3 — Rear-end collision A-6
- Type: frontal rear-end
- No visible braking marks (ABS)
- EDR available shows real speed
- Demonstrates "ABS without marks" case handling

---

## Useful Commands

```bash
# Frontend
pnpm dev                          # start local
pnpm build                        # prod build
pnpm lint                         # eslint
pnpm typecheck                    # tsc --noEmit

# Backend
uvicorn main:app --reload         # start local
pytest tests/                     # tests
ruff check .                      # linter
mypy .                            # type check

# Ingest legal corpus
python scripts/ingest_corpus.py --source data/corpus_legal/

# Seed demo cases
python scripts/seed_demo_casos.py

# Generate PDF for a case
python -m reports.pdf_generator --caso-id <uuid>

# Verify audit trail
python -m audit.sigstore_signer --verify <hash>

# Deploy
vercel --prod                     # frontend
```

---

## Known Risks

| Risk | Mitigation |
|---|---|
| Live demo crashes on stage | Backup video recorded + secondary machine with local |
| LLM latency > 90s | Aggressive cache of outputs per demo case + parallelization |
| RAG cites non-existent article | Cross-verification before including citation in report |
| Anthropic API down during demo | Fallback to pre-computed outputs as last resort |
| OCR fails on unusual report formats | Demo cases with pre-processed reports, no live processing |
| Mapbox glitches on projector | Test on projector beforehand, fallback to screenshots |

---

## Technical Resources

### Documentation
- Anthropic API: https://docs.anthropic.com
- Mapbox GL JS: https://docs.mapbox.com/mapbox-gl-js/
- Qdrant: https://qdrant.tech/documentation/
- AEMET OpenData: https://opendata.aemet.es/dist/index.html

### Domain References
- Reglamento General de Circulación (BOE)
- Ley 35/2015 baremo (BOE)
- CRASH3 Model (McHenry, 1975) — public papers
- Stannard Baker Method — UNED Judicial Expert training
- UNE-EN 16775 Standard — Expert services requirements
- NHTSA crash test database: https://www.nhtsa.gov/crash-data-systems

---

## Team

- Loic
- Baptiste
- Javier

**Repository:** https://github.com/LoicCLIENT/Veridict
**Live Demo:** https://veridict-two.vercel.app
