# Inconsistencias Encontradas y Correcciones

Este documento detalla las inconsistencias encontradas en el README.md original y las correcciones aplicadas.

## 1. Modelos de IA Inexistentes

### Problema
El README menciona:
- **Claude Opus 4.7** - Este modelo no existe. La version actual es **Claude Opus 4.5** (claude-opus-4-5-20251101)
- **GPT-5** - Este modelo no esta disponible publicamente a fecha de mayo 2025

### Correccion Aplicada
- Cambiado a **Claude Opus 4.5** en todos los agentes
- Cambiado a **GPT-4o** para el Legal Reasoner (disponible y muy capaz)

### Archivos Modificados
- `apps/api/agents/forensic_analyst.py`
- `apps/api/agents/adjudicator.py`
- `apps/api/agents/devils_advocate.py`
- `apps/api/agents/report_writer.py`
- `apps/api/agents/legal_reasoner.py`

---

## 2. Nombre del Proyecto Inconsistente

### Problema
El README usa "crashforensics" como nombre del proyecto/repo, pero:
- El repositorio real se llama "Veridict"
- Las URLs mencionan crashforensics.vercel.app

### Correccion Aplicada
- Renombrado todo a **Veridict AI**
- El bucket R2 se llama `veridict-uploads`
- Metadata del proyecto usa "Veridict AI"

---

## 3. Estructura de Monorepo Incompleta

### Problema
El README menciona pnpm workspaces pero faltaba:
- `pnpm-workspace.yaml`
- Configuracion de TypeScript compartida
- Package.json raiz

### Correccion Aplicada
- Creado `pnpm-workspace.yaml` con configuracion de workspaces
- Creado `packages/types/` con tipos TypeScript compartidos
- Estructura lista para `pnpm install` desde la raiz

---

## 4. Dependencias Python Desactualizadas

### Problema
Algunas dependencias mencionadas pueden tener versiones incompatibles:
- LangGraph version muy nueva (0.0.20) puede no existir
- Algunas dependencias sin version especificada

### Correccion Aplicada
- Especificadas versiones minimas compatibles
- Agregadas dependencias faltantes (httpx, aiohttp)
- requirements.txt listo para instalar

---

## 5. Endpoints API Sin Implementar

### Problema
El README lista endpoints pero el repo estaba vacio.

### Correccion Aplicada
Implementados TODOS los endpoints:

```
POST   /api/casos                          ✓
GET    /api/casos                          ✓
GET    /api/casos/{id}                     ✓
DELETE /api/casos/{id}                     ✓
POST   /api/casos/{id}/upload/atestado     ✓
POST   /api/casos/{id}/upload/foto         ✓
POST   /api/casos/{id}/mediciones          ✓
POST   /api/casos/{id}/analizar            ✓
GET    /api/casos/{id}/estado              ✓
GET    /api/casos/{id}/dictamen            ✓
GET    /api/casos/{id}/pdf                 ✓
GET    /api/casos/{id}/audit               ✓
GET    /api/demo/casos                     ✓
POST   /api/demo/casos/{id}/reset          ✓
GET    /api/data/meteo                     ✓
GET    /api/data/via                       ✓
GET    /api/data/sol                       ✓
GET    /api/data/vehiculo                  ✓
```

---

## 6. Pipeline Multi-Agente No Implementado

### Problema
El diagrama del pipeline existia pero no habia codigo.

### Correccion Aplicada
Implementado completo con LangGraph-style orchestration:

1. **ForensicAnalyst** - Calculos CRASH3 y Stannard Baker
2. **LegalReasoner** - RAG sobre corpus legal
3. **Adjudicator** - Atribucion de culpa
4. **DevilsAdvocate** - Verificacion adversarial
5. **ReportWriter** - Generacion PDF UNE-EN 16775

---

## 7. Modulos de Fisica Faltantes

### Problema
El README menciona CRASH3, Stannard Baker, momentum pero no habia implementacion.

### Correccion Aplicada
Implementados con formulas reales:

- `physics/crash3.py` - Calculo EBS por deformacion
- `physics/stannard_baker.py` - Velocidad pre-frenada
- `physics/momentum.py` - Conservacion cantidad movimiento
- `physics/coefficients.py` - Base de datos coeficientes NHTSA

---

## 8. Casos Demo Vacios

### Problema
El README describe 3 casos demo pero no habia datos.

### Correccion Aplicada
Creados 3 casos demo completos con:
- Datos de vehiculos
- Mediciones C1-C6
- Versiones de conductores
- Resultados pre-calculados
- Cronologias
- Calculos fisicos
- Infracciones
- Veredictos

---

## 9. Frontend Basico

### Problema
No habia codigo de frontend.

### Correccion Aplicada
Implementado frontend completo con Next.js 15:

- Landing page
- Lista de casos
- Detalle de caso con tabs
- Formulario nuevo caso
- Componentes:
  - MapaReconstruccion (Mapbox)
  - CronologiaTimeline
  - CalculosFisicos
  - RazonamientoLegal

---

## Recomendaciones Adicionales

### Para Produccion

1. **Base de Datos**: Reemplazar almacenamiento en memoria por PostgreSQL/Supabase
2. **Autenticacion**: Implementar auth con Supabase Auth
3. **Rate Limiting**: Agregar limites de API
4. **Caching**: Implementar Redis para cache de llamadas LLM
5. **Monitoring**: Agregar Sentry para errores

### Para el Hackathon

1. **Videos Demo**: Grabar backup en OBS antes del pitch
2. **Fallbacks**: Tener outputs pre-computados si APIs fallan
3. **Testing**: Probar en el proyector del venue
4. **Timing**: Ensayar que el pipeline complete en < 90s

---

## Comandos de Inicio Rapido

```bash
# Frontend
cd apps/web
pnpm install
pnpm dev

# Backend (otra terminal)
cd apps/api
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload

# Acceder
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```
