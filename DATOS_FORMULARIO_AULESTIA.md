# Datos para rellenar el formulario — Caso Aulestia 21/05/2020

**Fuente:** `CASO_REAL_aulestia_atropello_mortal_IURGI.pdf` (peritaje IURGI/ITRASA)
**Biblioteca de imágenes:** `./biblioteca/` (80 fotos extraídas del PDF original)
**URL del formulario:** http://localhost:3001/casos/nuevo

---

## Bloque 0 — Encargo pericial

| Campo | Valor |
|---|---|
| Tipo de pericia | Atropello |
| Parte solicitante | Demandante |
| Solicitante | `Juzgado de Instrucción de Markina-Xemein` |
| Procedimiento | `Diligencias previas — Aulestia 21052020` |

### Preguntas (3, una por una con "+ Añadir pregunta")

```
C1. Determinar la velocidad real del turismo en el momento de la colisión contra el ciclista.
```

```
C2. Establecer si el accidente era evitable cumpliendo la normativa de circulación.
```

```
C3. Indicar la conducta del conductor del turismo respecto al límite de velocidad y la atención debida.
```

---

## Bloque 1 — Datos del siniestro

| Campo | Valor |
|---|---|
| Fecha | `2020-05-21` |
| Hora | `20:38` |
| Tipo de colisión | Atropello |
| Dirección / p.k. | `Barrio Zubero, Aulestia, Bizkaia` |
| Latitud | `43.3300` |
| Longitud | `-2.6203` |

---

## Bloque 2 — Vehículos implicados

### Vehículo A (turismo investigado)

| Campo | Valor |
|---|---|
| Matrícula | `3526-BKL` |
| Marca | `SEAT` |
| Modelo | `Ibiza` |
| Año | `2018` |
| Color | `blanco` |
| Conductor | `JME (vecino de la zona, conoce el trazado y la limitación)` |

### Vehículo B (víctima — bicicleta) — pulsa "+ Añadir vehículo"

| Campo | Valor |
|---|---|
| Matrícula | `n/a (ciclo)` |
| Marca | `Orbea` |
| Modelo | `bicicleta deportiva (n.º bastidor 3773)` |
| Año | (vacío) |
| Color | `rojo` |
| Conductor | `IBU — sillín a 79 cm del suelo, manillar 55 cm de anchura. Circulaba descendente por la mitad derecha de la calzada. Marcas de derrape en cubierta trasera.` |

---

## Bloque 3 — Hechos del atestado

| Campo | Valor |
|---|---|
| Nº atestado | `Ertzaintza Aulestia 21052020` |
| Cuerpo actuante | Ertzaintza |
| Huellas de frenada | **Sí, hay huellas** (huella ciclista 8 m) |
| Meteorología | `tarde clara, asfalto seco` |
| Estado calzada | `seco` |
| Visibilidad | `diurna pero curva con visibilidad reducida (efectiva 26,5 m)` |

### Velocidades declaradas (pulsa "+ Añadir")

| Vehículo | km/h | Fuente |
|---|---|---|
| A | 20 | Declaración del conductor |

### Declaraciones — texto a copiar

```
El conductor del turismo declara que circulaba entre 10 y 20 km/h ascendiendo una pendiente del 9 al 11,6 %. Manifiesta que vio al ciclista y accionó el freno al máximo, pero en el momento del impacto el turismo no estaba detenido. El atestado consigna expresamente que "no se observan huellas de frenado" del turismo, pese a la frenada plena declarada. La huella de 8 metros, que finaliza a 1,2 m del borde de la vía e inicia a menos de 1 m del mismo, corresponde al CICLISTA bajando, no al turismo.
```

### Observaciones del atestado — texto a copiar

```
Características del lugar (medidas in situ por el perito instructor):
- Anchura de la calzada: 3,10 a 3,20 m.
- Pendiente: entre 9 % y 11,6 % (ascendente para el turismo, descendente para el ciclista).
- Distancia de visibilidad efectiva: 26,5 m lineales (>30 m por la trayectoria curva).
- Coeficiente de adherencia neumático-asfalto estimado: μ = 0,75.
- Existe una zona terriza diáfana de varios metros de anchura y longitud a la derecha del turismo, con desnivel máximo de 4 cm, que habría permitido una maniobra evasiva sin riesgo.
- Límite de velocidad en el lugar: señal específica R-301 de 20 km/h en la entrada al Barrio Zubero auzoa.
- En 2020 NO existía aún el límite genérico de 30 km/h en vía urbana (introducido por el RD 970/2020 vigente desde el 11/05/2021); el genérico vigente era 50 km/h.
```

---

## Bloque 4 — Lesiones (pulsa "+ Añadir")

| Ocupante | Vehículo | Zona corporal | Gravedad | Días baja |
|---|---|---|---|---|
| `IBU` | B | `cabeza (lesiones cefálicas letales)` | Fallecimiento | (vacío) |

### Secuelas — texto a copiar (si el form lo permite)

```
Lesiones cefálicas incompatibles con la vida según autopsia. Trayectoria del cuerpo del ciclista tras el impacto: contacto inicial con paragolpes delantero, deslizamiento sobre el capó (impronta visible en chapa), impacto contra el parabrisas delantero lado derecho y hendidura en el techo extremo derecho del turismo. Patrón de impactos compatible con WAD (Wrap Around Distance) ≥ 1,8 m, propio de velocidades del orden de 45-60 km/h en colisión turismo-ciclista.
```

---

## Bloque 5 — Biblioteca visual

Arrastra desde la carpeta `./biblioteca/` al drop zone violeta del formulario.

### Mínimo recomendado (7 fotos clave)

| Archivo | Página PDF | Qué muestra |
|---|---|---|
| `p13_x109.png` | 13 | Señal R-301 de 20 km/h en Zubero auzoa |
| `p11_x098.png` | 11 | Carretera rural en curva (escena) |
| `p10_x092.png` | 10 | Calzada con pieza desprendida |
| `p28_x196.png` | 28 | Diagrama WAD puntos impacto ciclista |
| `p20_x156.png` | 20 | Cálculo SamRAT distancia detención 20 km/h |
| `p21_x160.png` | 21 | Cálculo SamRAT distancia detención 30 km/h |
| `p23_x170.png` | 23 | Extracto del atestado Ertzaintza |

### Modo bestia (demo impresionante)

Selecciona TODAS las 80 fotos de `./biblioteca/` y arrástralas. El BibliotecaFotosAgent las indexará una a una con visión Claude (~5-7 s por foto, total ~7 min) y al generar el informe el orquestador hará búsquedas reales sobre el catálogo completo.

> ⚠️ Coste estimado: ~$1.5-2 USD en la API (80 imágenes × clasificación + 15-20 tool calls del Perito).

---

## Resumen rápido — copiar para chuleta

```
ENCARGO: atropello / demandante
SOLICITANTE: Juzgado Instrucción Markina-Xemein
PROCEDIMIENTO: Diligencias previas Aulestia 21052020
FECHA: 2020-05-21 20:38
LUGAR: Barrio Zubero, Aulestia, Bizkaia · 43.3300, -2.6203
VEHÍCULO A: SEAT Ibiza 2018 blanco · 3526-BKL · conductor JME (vecino)
VEHÍCULO B: Bici Orbea roja · ciclista IBU (sillín 79 cm, manillar 55 cm)
ATESTADO: Ertzaintza · huellas SÍ (ciclista 8 m) · sin huella turismo
VELOCIDAD DECLARADA: A=20 km/h (declaración)
LESIÓN: IBU · cabeza · fallecimiento
NORMATIVA CLAVE: Art. 3 RGC, Art. 45 RGC, Art. 46.1.b RGC, Principio de confianza
RD 970/2020: NO vigente a 21/05/2020
```

---

**Fin del documento.** Cuando termines de rellenar y le des a "Generar borrador", abre el tab "Razonamiento" para ver al Perito Opus 4.7 invocando los specialists en directo.
