# Veridict AI

> Reconstrucción forense automatizada de accidentes de tráfico.
> Hackathon Nexforge 2026 · Track Open · Deadline: 3 mayo 23:00 GMT+2

---

## TL;DR

Sistema multi-agente que recibe datos de un accidente (atestado, fotos, mediciones del perito) y devuelve un dictamen pericial en formato UNE-EN 16775 con cálculos físicos justificados (CRASH3, Stannard Baker), citas legales del corpus español y verificación adversarial — todo en menos de 90 segundos.

**Output del demo:** web app desplegada en Vercel con 2-3 casos pre-cargados. Pulsas un caso → procesa en vivo → muestra dictamen completo con mapa animado, cronología, cálculos, razonamiento legal y PDF descargable.

---

## Setup en 5 minutos

### Requisitos
- Node.js 20+
- Python 3.11+
- pnpm (`npm install -g pnpm`)
- Docker (opcional, para Qdrant local)
- Git

### Cuentas necesarias (todos los miembros del equipo)
Crear ya, antes de empezar el viernes:

- [ ] Anthropic API → https://console.anthropic.com (créditos para Claude Opus 4.7)
- [ ] OpenAI API → https://platform.openai.com (GPT-5 + embeddings)
- [ ] Mapbox → https://account.mapbox.com (free tier 50k req/mes)
- [ ] AEMET OpenData → https://opendata.aemet.es/centrodedescargas/altaUsuario
- [ ] Qdrant Cloud → https://cloud.qdrant.io (free tier 1GB)
- [ ] Supabase → https://supabase.com (free tier suficiente)
- [ ] Vercel → https://vercel.com (deploy frontend)
- [ ] Cloudflare → https://dash.cloudflare.com (R2 para storage)
- [ ] GitHub repo → privado, los 3 con acceso

### Clone y arranque

```bash
git clone git@github.com:[ORG]/crashforensics.git
cd crashforensics

# Variables de entorno (pedir a Loic el .env real)
cp .env.example .env

# Frontend
cd apps/web
pnpm install
pnpm dev          # http://localhost:3000

# Backend (terminal aparte)
cd apps/api
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn main:app --reload     # http://localhost:8000

# Vector DB local (opcional, si no usáis Qdrant Cloud)
docker run -p 6333:6333 qdrant/qdrant
```

---

## Stack

### Frontend
- **Next.js 15** (App Router)
- **TypeScript** strict
- **Tailwind CSS** + **shadcn/ui**
- **Mapbox GL JS** para mapa de reconstrucción
- **Recharts** para gráficos físicos
- **Framer Motion** para slider temporal y animaciones
- **react-pdf** para generación PDF
- **Zustand** para estado global

### Backend
- **Python 3.11**
- **FastAPI** + **uvicorn**
- **Pydantic v2** validación
- **NumPy + SciPy + filterpy** procesamiento físico
- **LangGraph** orquestación multi-agente
- **LangChain** para RAG
- **Pint** unidades físicas
- **Tesseract** OCR atestados
- **Pillow** procesamiento imágenes

### LLMs y datos
- **Claude Opus 4.7** (Anthropic) → razonamiento principal
- **GPT-5** (OpenAI) → verificación cruzada
- **Claude Vision** → análisis cualitativo de fotos
- **OpenAI text-embedding-3-large** → embeddings legales
- **Qdrant** → vector DB

### Infra
- **Vercel** → frontend
- **Railway o Render** → backend FastAPI
- **Supabase** → PostgreSQL + Auth + Storage
- **Cloudflare R2** → archivos pesados (PDFs, fotos)
- **Sigstore** → audit trail criptográfico

---

## Variables de entorno

`.env.example`:

```bash
# LLMs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Datos públicos
AEMET_API_KEY=eyJhbGc...
MAPBOX_ACCESS_TOKEN=pk.eyJ...

# Storage
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET=crashforensics-uploads

# Vector DB
QDRANT_URL=https://xxx.cloud.qdrant.io
QDRANT_API_KEY=...
QDRANT_COLLECTION=corpus_trafico_es

# Backend
DATABASE_URL=postgresql://...
API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Sigstore (opcional, usa OIDC público)
SIGSTORE_REKOR_URL=https://rekor.sigstore.dev
```

---

## Estructura del repo

```
crashforensics/
├── apps/
│   ├── web/                    # Next.js frontend
│   │   ├── app/
│   │   │   ├── page.tsx              # Landing
│   │   │   ├── casos/
│   │   │   │   ├── nuevo/page.tsx    # Formulario nuevo caso
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx      # Dictamen final
│   │   │   │       └── procesando/page.tsx
│   │   │   └── pipeline/page.tsx     # Mockup educativo
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn
│   │   │   ├── MapaReconstruccion.tsx
│   │   │   ├── CronologiaTimeline.tsx
│   │   │   ├── CalculosFisicos.tsx
│   │   │   ├── RazonamientoLegal.tsx
│   │   │   └── DictamenPDF.tsx
│   │   └── lib/
│   │       ├── api.ts                # cliente API
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
│       │   ├── graph.py              # LangGraph orchestration
│       │   ├── forensic_analyst.py
│       │   ├── legal_reasoner.py
│       │   ├── adjudicator.py
│       │   ├── devils_advocate.py
│       │   └── report_writer.py
│       ├── physics/
│       │   ├── crash3.py             # EBS por deformación
│       │   ├── stannard_baker.py     # Velocidad pre-frenada
│       │   ├── momentum.py           # Conservación cantidad mov.
│       │   ├── kalman.py             # Filtros para fusión sensores
│       │   ├── biomechanics.py       # Delta-V, AIS, Prasad-Mertz
│       │   └── coefficients.py       # Tabla A/B de NHTSA
│       ├── extract/
│       │   ├── atestado_ocr.py       # OCR del atestado PDF
│       │   ├── parte_amistoso.py     # OCR + parser
│       │   └── vision.py             # Claude Vision para fotos
│       ├── data/
│       │   ├── aemet.py              # Cliente AEMET
│       │   ├── dgt.py                # Datos DGT
│       │   ├── osm.py                # OpenStreetMap Overpass
│       │   └── suncalc.py            # Posición solar
│       ├── rag/
│       │   ├── ingest.py             # Carga corpus a Qdrant
│       │   ├── retrieve.py           # Búsqueda con filtros
│       │   └── corpus/               # PDFs descargados del BOE
│       ├── reports/
│       │   ├── pdf_generator.py      # PDF formato UNE-EN 16775
│       │   └── plantillas/
│       └── audit/
│           └── sigstore_signer.py    # Firma criptográfica
│
├── packages/
│   ├── types/                  # tipos TypeScript compartidos
│   └── physics-validators/     # validaciones cliente+server
│
├── data/
│   ├── casos_demo/             # CASOS PRE-CARGADOS PARA LA DEMO
│   │   ├── caso_1_madrid_m30/
│   │   │   ├── atestado.pdf
│   │   │   ├── parte_amistoso.pdf
│   │   │   ├── fotos/
│   │   │   ├── mediciones.json
│   │   │   └── ground_truth.json    # dictamen perito real
│   │   ├── caso_2_atropello_alcala/
│   │   └── caso_3_alcance_a6/
│   └── corpus_legal/           # PDFs del BOE
│
├── scripts/
│   ├── ingest_corpus.py        # Carga corpus legal a Qdrant
│   ├── seed_demo_casos.py      # Pre-carga casos demo en DB
│   └── grabar_demo.sh          # OBS automation
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEMO_SCRIPT.md          # Guion del pitch
│   └── QA_PREP.md              # 10 preguntas del jurado
│
├── .env.example
├── pnpm-workspace.yaml
├── README.md                   # ESTE ARCHIVO
└── DEMO_BACKUP.mp4             # Video grabado por si falla en directo
```

---

## API Endpoints

Base URL: `http://localhost:8000` (dev) · `https://api.crashforensics.app` (prod)

### Casos

```
POST   /api/casos                          # Crear caso
GET    /api/casos                          # Listar casos
GET    /api/casos/{id}                     # Detalle caso
DELETE /api/casos/{id}                     # Eliminar
```

### Upload

```
POST   /api/casos/{id}/upload/atestado     # Sube PDF atestado → OCR
POST   /api/casos/{id}/upload/parte        # Sube parte amistoso → OCR
POST   /api/casos/{id}/upload/foto         # Sube foto → Claude Vision
POST   /api/casos/{id}/mediciones          # Mediciones manuales perito
```

### Análisis

```
POST   /api/casos/{id}/analizar            # Lanza pipeline multi-agente (async)
GET    /api/casos/{id}/estado              # Polling progreso
GET    /api/casos/{id}/dictamen            # Dictamen completo cuando listo
GET    /api/casos/{id}/pdf                 # Descarga PDF formato UNE-EN 16775
GET    /api/casos/{id}/audit               # Audit trail Sigstore
```

### Datos públicos (cacheados)

```
GET    /api/data/meteo?lat=&lon=&t=        # AEMET
GET    /api/data/via?lat=&lon=             # DGT + OSM
GET    /api/data/sol?lat=&lon=&t=          # SunCalc
GET    /api/data/vehiculo?modelo=          # Coeficientes A/B
```

### Demo

```
GET    /api/demo/casos                     # Lista 2-3 casos pre-cargados
POST   /api/demo/casos/{id}/reset          # Resetea estado para nueva demo
```

---

## Modelo de datos

### Caso

```typescript
{
  id: uuid,
  estado: 'creado' | 'procesando' | 'completado' | 'escalado_humano',
  fecha_accidente: timestamp,
  ubicacion: { lat: number, lon: number },
  tipo_colision: 'frontal' | 'lateral' | 'alcance' | 'atropello',
  vehiculos: [
    {
      id: 'A' | 'B',
      matricula: string,
      modelo: string,
      masa_kg: number,
      coef_rigidez_a: number,
      coef_rigidez_b: number,
      mediciones_C: [number, number, number, number, number, number],  // C1-C6
      ancho_zona_dañada_cm: number,
      version_conductor: string  // declaración del conductor
    }
  ],
  documentos: Documento[],
  fotos: Foto[],
  contexto: {
    meteo: AemetData,
    via: ViaData,
    sol: SolData
  },
  resultado: {
    cronologia: Evento[],
    calculos: CalculoFisico[],
    infracciones: Infraccion[],
    veredicto: { culpa_a: number, culpa_b: number, confidence: number },
    compatibilidad_versiones: { a: boolean, b: boolean, justificacion: string },
    devils_advocate_passed: boolean,
    pdf_url: string,
    sigstore_hash: string
  }
}
```

---

## Pipeline multi-agente (LangGraph)

```
[Datos del caso completos]
        ↓
[Auto-extract] ─── AEMET, DGT, OSM, SunCalc en paralelo
        ↓
[Forensic Analyst] ─── usa Claude Opus 4.7
   └→ Calcula: CRASH3, Stannard Baker, momentum
   └→ Devuelve cronología JSON estructurada
        ↓
[Legal Reasoner] ─── usa GPT-5 + RAG Qdrant
   └→ Busca artículos RGC/LSV aplicables
   └→ Recupera jurisprudencia CENDOJ
   └→ Devuelve infracciones con citas
        ↓
[Adjudicator] ─── usa Claude Opus 4.7
   └→ Calcula % culpa
   └→ Asigna confidence score
        ↓
   ┌────┴────┐
   │ ≥ 0.85  │ < 0.85
   ↓         ↓
[Devil's    [Escalar
 Advocate]   humano]
   ↓
   ├─ verificar conservación momento
   ├─ verificar coherencia EBS vs marcas frenada
   ├─ verificar compatibilidad versiones
   └─ verificar coherencia biomecánica
   ↓
   ┌────┴────┐
   │ pasa    │ refuta
   ↓         ↓
[Report    [Escalar
 Writer]    humano]
   ↓
[PDF UNE-EN 16775]
   ↓
[Firma Sigstore]
```

---

## Datasets a cargar (RAG legal)

Descargar de https://www.boe.es y procesar:

- [ ] **Reglamento General de Circulación** → `BOE-A-2003-23514`
- [ ] **Ley sobre Tráfico, Circulación y Seguridad Vial** → `BOE-A-2015-11722`
- [ ] **Ley 35/2015 (baremo)** → `BOE-A-2015-10197`
- [ ] **Real Decreto 1486/2018** → `BOE-A-2018-17628`

Y de https://www.poderjudicial.es/search:
- [ ] **150-300 sentencias CENDOJ** → filtros: civil + tráfico + 2020-2026

Comando para cargar todo el corpus:

```bash
python scripts/ingest_corpus.py --source data/corpus_legal/ --collection corpus_trafico_es
```

---

## Casos demo a preparar

Tienen que estar 100% funcionales y ensayados. Cada caso = directorio en `data/casos_demo/` con:

- `atestado.pdf` (real o sintético verosímil)
- `parte_amistoso.pdf` opcional
- `fotos/` con fotos del lugar y daños
- `mediciones.json` con mediciones del perito (C1-C6, longitud frenada, etc.)
- `ground_truth.json` con el dictamen del perito real (para comparar)

### Caso 1 — Recomendado: Cambio de carril sin señalizar M-30
- Tipo: alcance lateral
- Conductor A circula 67 km/h en zona 50, lluvia
- Conductor B cambia carril sin señalizar
- Resultado esperado: 65% culpa A, 35% culpa B
- Compatibilidad: ambas versiones parcialmente compatibles

### Caso 2 — Recomendado: Atropello en paso de cebra Alcalá
- Tipo: atropello peatón
- Conductor a 52 km/h en zona 30 según deformaciones
- Conductor declara 30 km/h
- Resultado esperado: versión conductor INCOMPATIBLE con física
- La pieza estrella del demo

### Caso 3 — Recomendado: Alcance trasero A-6
- Tipo: alcance frontal
- Sin huellas frenada visibles (ABS)
- EDR disponible muestra velocidad real
- Demuestra el manejo del caso "ABS sin huellas"

Pre-cargar en DB con:
```bash
python scripts/seed_demo_casos.py
```

---

## Convenciones del equipo

### Branches

```
main                  # producción (deploy automático Vercel)
└─ dev                # integración
   ├─ feat/<nombre>   # features
   ├─ fix/<nombre>    # bugfixes
   └─ demo/<nombre>   # cosas específicas del demo
```

### Commits

Conventional commits cortos:
```
feat(api): add forensic analyst agent
fix(web): mapa carga lento en safari
chore: update env example
demo: caso 2 ready for rehearsal
```

### Pull requests

- Self-merge OK durante hackathon
- Pegar screenshot/video si afecta UI
- No mergear nada que rompa `main` después del sábado 18:00

### Comms

- **Slack/Discord** comms generales (canal `#crashforensics`)
- **Linear o GitHub Projects** tareas
- **Standup cada 3h** los 3 juntos en persona o call corta

---

## Comandos útiles

```bash
# Frontend
pnpm dev                          # arrancar local
pnpm build                        # build prod
pnpm lint                         # eslint
pnpm typecheck                    # tsc --noEmit

# Backend
uvicorn main:app --reload         # arrancar local
pytest tests/                     # tests
ruff check .                      # linter
mypy .                            # type check

# Pipeline LangGraph standalone
python -m agents.graph --caso data/casos_demo/caso_1_madrid_m30

# Ingest corpus legal
python scripts/ingest_corpus.py --source data/corpus_legal/

# Seed casos demo
python scripts/seed_demo_casos.py

# Generar PDF de un caso
python -m reports.pdf_generator --caso-id <uuid>

# Verificar audit trail
python -m audit.sigstore_signer --verify <hash>

# Deploy
vercel --prod                     # frontend
railway up                        # backend (o render deploy)
```

---

## Definición de "demo listo"

El proyecto está listo cuando TODOS estos puntos están checked:

### Funcional
- [ ] 2-3 casos demo pre-cargados ejecutan end-to-end sin errores
- [ ] Pipeline multi-agente completo en menos de 90 segundos por caso
- [ ] Mapa Mapbox renderiza con trayectorias animadas
- [ ] Slider temporal sincroniza mapa, cronología y gráficos
- [ ] PDF descargable se genera correctamente para los 3 casos
- [ ] Audit trail Sigstore visible y verificable
- [ ] Compatibilidad de versiones funciona y produce output convincente

### Demo en vivo
- [ ] Web app desplegada en Vercel pública con URL bonita
- [ ] Casos demo accesibles en menos de 2 clicks desde landing
- [ ] Pantalla de procesamiento muestra progreso real-time
- [ ] Dictamen final muestra TODA la información (no scroll infinito)
- [ ] Funciona en pantalla de proyector sin glitches

### Backup
- [ ] Video MP4 de 90s con la demo perfecta grabado en OBS
- [ ] Screenshots de cada pantalla en alta resolución
- [ ] Pitch deck (PowerPoint o Figma) con 10 slides
- [ ] Demo backup local funcionando offline en laptop secundaria

### Submission Devpost
- [ ] Working prototype URL pública
- [ ] Repo GitHub público con README cuidado
- [ ] Pitch deck subido
- [ ] Demo video de 3-5 min en YouTube unlisted
- [ ] Project summary escrito (500-1000 palabras)

### Pitch
- [ ] Script ensayado 30+ veces
- [ ] Las 10 preguntas del jurado con respuestas memorizadas
- [ ] Quién habla en cada minuto definido
- [ ] Plan B si la demo en vivo falla (lanzar video)

---

## Out of scope (NO construir esto)

Cosas que NO van al MVP de hackathon. Se mencionan en pitch como "versión productiva":

- ❌ Integración real con Bosch CDR (hardware físico)
- ❌ Fine-tuning propio de YOLO o modelos CV (usar Claude Vision)
- ❌ App móvil nativa (solo web)
- ❌ Multi-tenant con login (un solo "perito demo")
- ❌ Integraciones con sistemas de aseguradoras
- ❌ Validación judicial real / certificación ISO 27001
- ❌ Procesamiento real-time de telemetría EDR (datos pre-cargados)
- ❌ Soporte multi-idioma (solo español)
- ❌ Pagos / suscripciones
- ❌ Onboarding completo

---

## Riesgos conocidos

| Riesgo | Mitigación |
|---|---|
| Demo en vivo se rompe en escenario | Video backup grabado + máquina secundaria con local |
| Latencia LLM > 90s | Cache agresivo de outputs por caso demo + paralelización |
| RAG cita artículo inexistente | Verificación cruzada antes de incluir cita en informe |
| Anthropic API down durante demo | Fallback a OpenAI + outputs pre-computados como último recurso |
| OCR atestado falla en formatos raros | Casos demo con atestados pre-procesados, no procesar live |
| Mapbox glitchea en proyector | Probar en proyector el sábado, fallback a screenshots |
| Pregunta técnica imprevista en Q&A | Memorizar las 10 preguntas, comodín "buen punto, va a roadmap" |

---

## Recursos rápidos

### Documentación técnica
- LangGraph: https://langchain-ai.github.io/langgraph/
- Claude API: https://docs.anthropic.com
- Mapbox GL JS: https://docs.mapbox.com/mapbox-gl-js/
- Qdrant: https://qdrant.tech/documentation/
- AEMET OpenData: https://opendata.aemet.es/dist/index.html

### Referencias del dominio
- Reglamento General de Circulación (BOE)
- Ley 35/2015 baremo (BOE)
- Modelo CRASH3 (McHenry, 1975) — papers públicos
- Método Stannard Baker — formación UNED Perito Judicial
- Norma UNE-EN 16775 — Requisitos servicios periciales
- NHTSA crash test database: https://www.nhtsa.gov/crash-data-systems

### Inspiración UI
- Linear (linear.app) — densidad de información
- Stripe Atlas (stripe.com/atlas) — premium feel
- Vercel Dashboard — dark mode pro
- Datadog APM — visualización de pipelines

---

## Contacto

- Loic — `[handle]`
- Baptiste — `[handle]`
- Javier — `[handle]`

Repo: `github.com/[org]/crashforensics`
Demo: `crashforensics.vercel.app` (cuando esté deployed)
Devpost: `devpost.com/software/crashforensics-ai`

---

**Última actualización:** Viernes mañana, día 1 de hackathon. Editar libremente.
