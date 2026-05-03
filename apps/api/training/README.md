# Sistema de Entrenamiento de Visualizaciones

Este directorio contiene herramientas para iterar y mejorar los agentes de visualizacion (SVG/2D) comparando con documentos profesionales de peritaje.

## Workflow de Entrenamiento

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Generar SVG    │ --> │  Comparar con    │ --> │  Obtener        │
│  con agentes    │     │  referencia      │     │  mejoras        │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                                                │
         │                                                v
         │                                       ┌─────────────────┐
         └─────────────────────────────────────  │  Aplicar        │
                                                 │  mejoras        │
                                                 └─────────────────┘
```

## Scripts Disponibles

### 1. `iterate.py` - Iteracion Rapida (RECOMENDADO)

El script mas simple para empezar:

```bash
cd apps/api
python training/iterate.py
```

Con descripcion del documento de referencia:
```bash
python training/iterate.py --reference "El documento profesional usa vehiculos 3D renderizados, flechas de velocidad con degradado, escala grafica visible..."
```

Modo interactivo:
```bash
python training/iterate.py --interactive
```

### 2. `train_visualizations.py` - Entrenamiento Completo

Para comparar con imagenes de referencia reales:

```bash
# Con imagen de referencia
python training/train_visualizations.py --reference path/to/peritaje_page.png

# Con directorio de imagenes
python training/train_visualizations.py --reference path/to/reference_images/

# Multiples iteraciones
python training/train_visualizations.py --reference images/ --iterations 3
```

### 3. `compare_visualizations.py` - Generar Reporte HTML

Genera un HTML interactivo con comparacion lado a lado:

```bash
python training/compare_visualizations.py \
    --svg outputs/croquis_20240101_120000.svg \
    --reference path/to/reference_images/ \
    --analysis outputs/iteration_1.json \
    --output comparison.html
```

## Preparar Imagenes de Referencia

Para obtener las mejores mejoras, extrae imagenes del documento de peritaje profesional:

1. **Desde PDF**: Usa herramientas como `pdf2image` o captura de pantalla
2. **Nombrar archivos**: `croquis_01.png`, `croquis_02.png`, etc.
3. **Colocar en directorio**: `training/reference/`

Ejemplo de estructura:
```
training/
├── reference/
│   ├── croquis_general.png
│   ├── simulacion_3d.png
│   ├── trayectorias.png
│   └── impacto_detalle.png
├── outputs/           # SVGs e informes generados
└── *.py              # Scripts
```

## Flujo de Trabajo Tipico

### Dia 1: Primera Iteracion

```bash
# 1. Generar primera comparacion
python training/iterate.py --reference "Documento profesional con vehiculos 3D..."

# 2. Revisar outputs/improvements_XXXX.json
# 3. Ver el codigo sugerido en 'funcion_mejorada'
```

### Dia 2: Aplicar Mejoras

```bash
# 1. Editar physics/croquis.py con las mejoras sugeridas
# 2. Ejecutar otra iteracion para validar
python training/iterate.py

# 3. Comparar SVGs: antes vs despues
```

### Dia 3: Iteracion Avanzada

```bash
# 1. Extraer imagenes del PDF profesional
# 2. Ejecutar con imagenes reales
python training/train_visualizations.py --reference reference/

# 3. Generar reporte HTML
python training/compare_visualizations.py \
    --svg outputs/croquis_latest.svg \
    --reference reference/ \
    --output report.html

# 4. Abrir report.html en navegador
```

## Que Mejoras Esperar

Claude analizara y sugerira mejoras como:

| Aspecto | Actual | Objetivo |
|---------|--------|----------|
| Vehiculos | Rectangulos basicos | Siluetas realistas |
| Perspectiva | 2D plano | Vista isometrica/3D |
| Flechas | Lineas simples | Degradados, puntas elaboradas |
| PDI | Circulo verde | Icono de explosion/impacto |
| Escala | Solo en leyenda | Barra grafica visible |
| Huellas | Lineas basicas | Patrones de neumatico |

## Outputs

Cada iteracion genera:
- `iteration_TIMESTAMP.svg` - SVG generado
- `improvements_TIMESTAMP.json` - Analisis y codigo sugerido

## Tips

1. **Ser especifico en la referencia**: Describe detalles del documento profesional
2. **Iterar incrementalmente**: Aplica 1-2 mejoras por iteracion
3. **Guardar versiones**: Haz backup de croquis.py antes de modificar
4. **Validar codigo**: El codigo sugerido puede necesitar ajustes
