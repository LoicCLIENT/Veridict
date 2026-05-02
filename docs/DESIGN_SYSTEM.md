# Veridict — Design System

> Documento sagrado. Toda decisión de UI debe respetar estas reglas.

---

## Filosofía

- **Minimalista**: Solo lo necesario. Nada decorativo sin función.
- **Práctico**: Un perito de 55 años debe entenderlo sin manual.
- **Moderno**: Estética startup europea, no "AI genérico americano".
- **Serio**: Herramienta profesional, no juguete tecnológico.

---

## Paleta de Colores

Solo dos colores. Sin excepciones.

### Verde Oscuro — `#1F3329`
```
RGB: 31, 51, 41
HSL: 150°, 24%, 16%
```
- **Uso**: Fondos, tarjetas, paneles, sidebars, superficies amplias
- **Proporción**: 85% de cualquier pantalla
- **Sensación**: Autoridad técnica, seriedad, confianza

### Lima Amarillo — `#C2E94B`
```
RGB: 194, 233, 75
HSL: 75°, 79%, 60%
```
- **Uso EXCLUSIVO**:
  - Botón principal de acción (1 por pantalla máximo)
  - Porcentajes de culpa en dictámenes
  - Scores de confianza
  - Badges "validado" / "completado"
  - Logo
  - Iconos de status positivo
- **Proporción**: 15% máximo
- **Sensación**: Energía, modernidad, punto focal

### Colores Complementarios (derivados)

```css
--veridict-green-900: #1F3329;  /* Base */
--veridict-green-800: #2A4435;  /* Cards elevadas */
--veridict-green-700: #355541;  /* Hover states */
--veridict-green-600: #40664D;  /* Bordes activos */
--veridict-green-500: #4B7759;  /* Texto secundario */

--veridict-lime: #C2E94B;       /* Acento */
--veridict-lime-hover: #D4F06A; /* Hover en botones lima */
--veridict-lime-muted: #C2E94B33; /* Backgrounds sutiles (20% opacity) */

--veridict-white: #F5F5F0;      /* Texto principal */
--veridict-gray: #A3A99E;       /* Texto secundario/muted */
--veridict-error: #E94B4B;      /* Errores (rojo que armoniza) */
```

---

## Proporciones Obligatorias

En CUALQUIER pantalla:

```
┌─────────────────────────────────┐
│                                 │
│         85% VERDE OSCURO        │
│         (fondos, cards)         │
│                                 │
│    ┌─────────────────────┐      │
│    │   15% LIMA MÁXIMO   │      │
│    │   (acentos puntuales)│     │
│    └─────────────────────┘      │
│                                 │
└─────────────────────────────────┘
```

**Regla de oro**: Si hay más de 3 elementos lima en viewport, sobra alguno.

---

## Tipografía

### Font Stack
```css
--font-sans: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: "JetBrains Mono", "Fira Code", monospace;
```

### Escala
```css
--text-xs: 0.75rem;    /* 12px - Labels, captions */
--text-sm: 0.875rem;   /* 14px - Body secundario */
--text-base: 1rem;     /* 16px - Body principal */
--text-lg: 1.125rem;   /* 18px - Subtítulos */
--text-xl: 1.25rem;    /* 20px - Títulos sección */
--text-2xl: 1.5rem;    /* 24px - Títulos página */
--text-3xl: 2rem;      /* 32px - Headlines */
--text-4xl: 2.5rem;    /* 40px - Hero solo landing */
```

### Pesos
- `400` — Texto normal
- `500` — Énfasis sutil, labels
- `600` — Títulos, botones
- `700` — Solo headlines hero

---

## Espaciado

Sistema de 4px base:

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
```

---

## Bordes y Radios

```css
--radius-sm: 6px;      /* Botones pequeños, badges */
--radius-md: 8px;      /* Cards, inputs */
--radius-lg: 12px;     /* Modales, paneles grandes */
--radius-xl: 16px;     /* Cards destacadas */

--border-subtle: 1px solid rgba(255, 255, 255, 0.06);
--border-visible: 1px solid rgba(255, 255, 255, 0.12);
```

---

## Sombras

Sombras sutiles, nada dramático:

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2);
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.25);
--shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.3);
```

---

## Gradientes con Ruido

Para fondos hero y secciones destacadas. Abstractos, no lineales.

```css
/* Gradiente base verde */
.gradient-hero {
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, #2A443580 0%, transparent 50%),
    radial-gradient(ellipse 60% 40% at 100% 100%, #35554120 0%, transparent 40%),
    #1F3329;
}

/* Overlay de ruido (aplicar con mix-blend-mode: overlay, opacity: 0.03) */
.noise-overlay {
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%' height='100%' filter='url(%23noise)'/%3E%3C/svg%3E");
}
```

---

## Componentes

### Botones

```
PRIMARIO (Lima) — Solo 1 por pantalla
┌──────────────────┐
│  Analizar caso   │  bg: #C2E94B, text: #1F3329, font-weight: 600
└──────────────────┘

SECUNDARIO (Outline)
┌──────────────────┐
│  Ver detalles    │  border: 1px solid rgba(255,255,255,0.2), text: #F5F5F0
└──────────────────┘

GHOST (Solo texto)
   Cancelar          text: #A3A99E, hover: text: #F5F5F0
```

### Cards

```
┌─────────────────────────────────┐
│                                 │  bg: #2A4435 (green-800)
│  Título                         │  border: 1px solid rgba(255,255,255,0.06)
│  Contenido...                   │  radius: 12px
│                                 │
└─────────────────────────────────┘
```

### Badges

```
Estado positivo:   bg: #C2E94B20, text: #C2E94B, border: none
Estado neutral:    bg: rgba(255,255,255,0.08), text: #A3A99E
Estado negativo:   bg: #E94B4B20, text: #E94B4B
```

### Inputs

```
┌─────────────────────────────────┐
│ Placeholder...                  │  bg: #2A4435
└─────────────────────────────────┘  border: 1px solid rgba(255,255,255,0.12)
                                     focus: border-color: #C2E94B
```

---

## Iconografía

- **Librería**: Lucide React (consistente, limpio)
- **Tamaño estándar**: 20px (w-5 h-5)
- **Stroke**: 1.5px
- **Color**: Heredar del texto padre, nunca hardcoded

---

## Animaciones

Sutiles, funcionales, nunca decorativas.

```css
--transition-fast: 150ms ease;
--transition-base: 200ms ease;
--transition-slow: 300ms ease;

/* Framer Motion defaults */
const fadeIn = { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { duration: 0.2 } }
const slideUp = { initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.3 } }
```

---

## Anti-patterns — PROHIBIDO

1. ❌ Gradientes lineales de colores
2. ❌ Badges tipo "Powered by AI" / "Beta" / "New"
3. ❌ Iconos decorativos sin función
4. ❌ Texto lorem ipsum o placeholder visible
5. ❌ Más de 1 botón lima por viewport
6. ❌ Sombras colored/glow
7. ❌ Bordes gruesos (>1px)
8. ❌ Animaciones que duren >400ms
9. ❌ Fondos blancos puros (#FFFFFF)
10. ❌ Grises azulados (usar grises verdosos)

---

## Layout Principles

### Jerarquía Visual
1. **Número/Dato clave** — Lo más grande, puede ser lima
2. **Título de sección** — Blanco, semi-bold
3. **Cuerpo explicativo** — Gris, regular
4. **Metadata** — Gris claro, pequeño

### Densidad
- Desktop: Respirado pero no vacío
- Datos técnicos: Pueden ser densos (es lo que esperan los peritos)
- Acciones: Siempre con espacio generoso

### Grid
```css
/* Container máximo */
max-width: 1280px;

/* Grid de contenido */
display: grid;
grid-template-columns: repeat(12, 1fr);
gap: 24px;
```

---

## Ejemplo de Pantalla Correcta

```
┌────────────────────────────────────────────────────────────┐
│ [Logo]                              [Nav items]    [User] │ Header: green-900
├────────────────────────────────────────────────────────────┤
│                                                            │
│   Caso #2024-0847                                         │
│   Colisión lateral M-30 km 12.4                           │
│                                                            │
│   ┌─────────────────────┐  ┌─────────────────────┐        │
│   │                     │  │  Culpa Vehículo A   │        │
│   │   [Mapa Mapbox]     │  │       ████████      │        │
│   │                     │  │        72%  ← LIMA  │        │
│   │                     │  │                     │        │
│   └─────────────────────┘  │  Confianza: 94%    │        │
│                            └─────────────────────┘        │
│                                                            │
│   ┌─────────────────────────────────────────────┐         │
│   │  Timeline cronológico                        │         │
│   │  ───●────────●────────●────────●───         │         │
│   └─────────────────────────────────────────────┘         │
│                                                            │
│                              [ Descargar PDF ]  ← LIMA    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Checklist Pre-Commit

Antes de commitear cualquier cambio de UI:

- [ ] ¿Proporción 85/15 verde/lima respetada?
- [ ] ¿Solo 1 botón lima visible?
- [ ] ¿Textos reales, no placeholders?
- [ ] ¿Animaciones <400ms?
- [ ] ¿Sin badges decorativos?
- [ ] ¿Jerarquía clara de información?
- [ ] ¿Funciona para un perito de 55 años?

---

*Última actualización: Mayo 2025*
*Este documento es ley. Las excepciones requieren justificación documentada.*
