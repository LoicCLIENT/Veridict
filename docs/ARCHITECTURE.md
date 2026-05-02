# Veridict AI - Architecture

## Propósito

Veridict AI es una herramienta de apoyo al perito forense de accidentes de tráfico.
Automatiza los cálculos físicos (CRASH3, Stannard Baker), reconstruye la cronología
del accidente e identifica los artículos del RGC/LSV aplicables, generando un informe
pericial en formato UNE-EN 16775.

**El sistema no atribuye culpa ni responsabilidad.** Esa es función exclusiva del
perito firmante y, en última instancia, del sistema judicial.

## Pipeline de análisis

```
Datos del caso
(mediciones C1-C6, declaraciones, fecha/ubicación)
        │
        ▼
[1. FORENSIC ANALYST]
   ├─ Cálculos CRASH3: EBS por deformación
   ├─ Cálculos Stannard Baker: velocidad por huella de frenada
   └─ Claude Sonnet → cronología forense (4-6 eventos)
        │
        ▼
[2. LEGAL REASONER]
   └─ Claude Sonnet → artículos RGC/LSV aplicables con citas BOE
        │
        ▼
[3. REPORT WRITER]
   ├─ Claude Sonnet → párrafo de conclusión técnica
   └─ ReportLab → PDF formato UNE-EN 16775 + hash SHA256
```

## Agentes

### 1. Forensic Analyst (Claude Sonnet)
- Recibe: mediciones C1-C6, masa, modelo de vehículo, declaraciones
- Ejecuta: CRASH3 (EBS por deformación), Stannard Baker (velocidad por frenada)
- Llama a Claude con los valores calculados para generar la cronología
- Devuelve: `cronologia[]`, `calculos[]`

### 2. Legal Reasoner (Claude Sonnet)
- Recibe: tipo de colisión, cálculos físicos, declaraciones
- Corpus legal embebido en prompt: Art. 74.1 RGC, Art. 72.1 RGC, Art. 54.1 RGC, Art. 65.3.a LSV
- Devuelve: `infracciones[]` con artículo, descripción, vehículo y referencia BOE

### 3. Report Writer (Claude Sonnet + ReportLab)
- Claude genera el párrafo de conclusión técnica (80-120 palabras, tono pericial)
- ReportLab monta el PDF con todas las secciones UNE-EN 16775
- SHA256 del PDF como firma de integridad
- Devuelve: `pdf_url`, `sigstore_hash`

## Estructura del informe PDF (UNE-EN 16775)

```
1. Datos del accidente (fecha, ubicación, tipo)
2. Vehículos implicados (matrícula, modelo, masa)
3. Cronología forense (T+0s … T+Ns)
4. Cálculos físicos (fórmula, resultado, justificación)
5. Artículos aplicables (RGC/LSV con referencia BOE)
6. Conclusión pericial (redactada por el sistema, firmada por el perito)
```

## Stack tecnológico

### Backend
- Python 3.13 + FastAPI + uvicorn
- Pydantic v2 para validación
- NumPy para cálculos físicos
- ReportLab para generación PDF

### AI
- Claude Sonnet 4.6 — cronología, infracciones, conclusión pericial
- Claude Opus 4.7 — (reservado para futura complejidad analítica)

### Infraestructura
- Vercel (frontend)
- Railway/Render (backend)
- Supabase (base de datos, en roadmap)
- Cloudflare R2 (almacenamiento PDFs, en roadmap)

## Modelos de datos principales

```python
Caso          → id, fecha, ubicación, tipo_colisión, vehículos[], resultado
Vehiculo      → id, matrícula, modelo, masa_kg, mediciones_C[6], ancho_zona, declaración
Resultado     → cronología[], cálculos[], infracciones[], pdf_url, sigstore_hash
CalculoFisico → nombre, fórmula, valor, unidad, justificación
Infraccion    → artículo, descripción, vehículo, fuente (BOE)
Evento        → timestamp (s), descripción
```
