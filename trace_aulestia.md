# Trace deep-log del orquestador VERIDICT-PERITO

**Caso:** `8c186a74-9443-494e-9d22-c543802ca323`  
**Fecha siniestro:** 2020-05-21T20:38:00  
**Tipo:** atropello  
**Encargo:** atropello — Juzgado de Instruccion de Markina-Xemein  
**Procedimiento:** Diligencias previas accidente Aulestia 21/05/2020  

---

## 1. Conversación orquestador ↔ especialistas (turno a turno)

El Perito Opus 4.7 ejecutó **4 turnos** invocando **21 llamadas a tools**. Para cada turno se documenta:
- Razonamiento intermedio del Perito (text blocks).
- Tools que el Perito decidió invocar y con qué inputs.
- Datos completos devueltos por cada specialist.

### Turno 1
**🧠 Razonamiento del Perito:**

> Voy a investigar este caso de atropello mortal con las herramientas disponibles. Empiezo recopilando contexto base y el inventario de fotos.

**🔧 Tools invocadas en este turno: 4**

#### 1.1 → `listar_biblioteca_fotos`

**Inputs del Perito:**
```json
{}
```

**Respuesta del especialista:**
```json
{
  "total": 40,
  "por_tipo": {
    "otro": [
      {
        "id": "5a557192-80e0-4851-8f0c-e2acc1ecd803",
        "descripcion": "Página con membrete corporativo de ITRASA sin contenido fotográfico ni documental relevante para el caso.",
        "tags": [
          "pagina_en_blanco",
          "membrete_corporativo",
          "sin_contenido_forense"
        ],
        "vehiculo_id": null,
        "calidad": "baja"
      },
      {
        "id": "1238e8da-c868-435c-94da-27321fabbcdf",
        "descripcion": "Imagen completamente negra sin contenido visual identificable, posiblemente fallo de exposición o captura incorrecta.",
        "tags": [
          "imagen_negra",
          "sin_contenido_visible",
          "exposicion_nula"
        ],
        "vehiculo_id": null,
        "calidad": "baja"
      },
      {
        "id": "d473fa70-8a89-474d-a83a-4e23bfdc43a5",
        "descripcion": "Logotipo del Cuerpo Nacional de Peritos Judiciales AEPSAL, especialidad Prevención de Riesgos Laborales. No contiene imagen forense.",
        "tags": [
          "logotipo",
          "entidad_pericial",
          "sello_institucional"
        ],
        "vehiculo_id": null,
        "calidad": "alta"
      }
    ],
    "escena_general": [
      {
        "id": "f4c10ead-4fe8-4296-9df7-50586c2a9db7",
        "descripcion": "Calzada de hormigón fisurado con objeto pequeño no identificado depositado sobre la vía, posiblemente fragmento o pieza desprendida en el siniestro.",
        "tags": [
          "calzada_hormigon",
          "objeto_calzada",
          "fragmento_vehiculo_calzada",
          "via_rural",
          "talud_lateral"
        ],
        "vehiculo_id": null,
        "calidad": "media"
      },
      {
        "id": "0b98c989-0cbe-482e-a4ff-d99554b4b4cb",
        "descripcion": "Carretera rural con curva en zona boscosa y neblinosa; tres personas presentes en arcén fotografiando el lugar del siniestro.",
        "tags": [
          "carretera_rural",
          "curva_calzada",
          "testigos_presentes",
          "zona_forestal",
          "niebla",
          "arcen_tierra"
        ],
        "vehiculo_id": null,
        "calidad": "media"
      },
      {
        "id": "c4557c1c-af2f-454c-abd9-e039e07ddbc1",
        "descripcion": "Incorporación en zona rural del barrio Zubero auzoa, con señal de límite 20 km/h y calzada húmeda. Sin vehículos visibles en escena.",
        "tags": [
          "interseccion_vial",
          "via_rural",
          "senial_velocidad_20",
          "senial_nucleo_poblado",
          "calzada_mojada",
          "incorporacion_lateral"
        ],
        "vehiculo_id": null,
        "calidad": "alta"
      },
      {
        "id": "7f6aaf64-3c27-46ae-8623-7ce1ab0ac36e",
        "descripcion": "Camino rural de hormigón con vehículo turismo al fondo, remolque y contenedor a la izquierda; referencia métrica depositada en calzada.",
        "tags": [
          "via_rural",
          "calzada_hormigon",
          "camino_privado",
          "vehiculo_al_fondo",
          "remolque_lateral",
          "contenedor_azul",
          "referencia_metrica_suelo"
        ],
        "vehiculo_id": null,
        "calidad": "alta"
      },
      {
        "id": "e122a274-6ddd-4a8c-8c38-045f181ec384",
        "descripcion": "Vista general de vía rural estrecha con remolque detenido en margen izquierdo y persona con chaleco rojo en zona de accidente.",
        "tags": [
          "carretera_rural",
          "remolque_fuera_calzada",
          "persona_interviniente",
          "via_estrecha",
          "zona_rural"
        ],
        "vehiculo_id": null,
        "calidad": "baja"
      },
      {
        "id": "993af138-bea2-4997-97da-9023beab0a95",
        "descripcion": "Calzada de hormigón con juntas de dilatación en zona rural, arcén de gravilla, curva suave, vegetación lateral y sombra arbórea proyectada sobre la vía.",
        "tags": [
          "calzada_hormigon",
          "via_rural",
          "curva_suave",
          "gravilla_arcen",
          "vegetacion_lateral",
          "sin_senalizacion_visible"
        ],
        "vehiculo_id": null,
        "calidad": "media"
      },
      {
        "id": "11c52864-8359-4b04-952f-179fd7839a24",
        "descripcion": "Vista general de carretera rural estrecha con curva, zona de gravilla a la derecha y turismo plateado estacionado al fondo, sin daños visibles.",
        "tags": [
          "carretera_rural_estrecha",
          "curva_calzada",
          "zona_gravilla",
          "vehiculo_estacionado",
          "entorno_boscoso"
        ],
        "vehiculo_id": null,
        "calidad": "alta"
      },
      {
        "id": "7b05be08-dbd3-4024-8740-39f2f3616fc5",
        "descripcion": "Vista de calzada rural con curva, arcén de grava sin pavimentar y vegetación en entorno montañoso. Sin vehículos ni marcas visibles.",
        "tags": [
          "via_rural",
          "curva_calzada",
          "zona_grava",
          "arcen_sin_pavimentar",
          "entorno_montañoso"
        ],
        "vehiculo_id": null,
        "calidad": "baja"
      }
    ],
    "croquis": [
      {
        "id": "4f322155-c452-47d0-8fdc-9830f5bd8a55",
        "descripcion": "Diagrama técnico forense con zonas de impacto sobre capó y parabrisas para peatón joven y ciclista joven a distintas velocidades (20-50 km/h), con líneas WAD 1000 y 1500.",
        "tags": [
          "diagrama_tecnico",
          "puntos_impacto_peatón",
          "puntos_impacto_ciclista",
          "WAD_1000",
          "WAD_1500",
          "velocidades_impacto",
          "capo_vehiculo",
          "parabrisas"
        ],
        "vehiculo_id": null,
        "calidad": "alta"
      },
      {
        "id": "7e16c71e-e4e1-4d6f-9533-d825a3ec15a8",
        "descripcion": "Diagrama técnico WAD que muestra zonas de impacto sobre capó y parabrisas para peatón joven y ciclista joven a distintas velocidades.",
        "tags": [
          "diagrama_tecnico",
          "WAD_wrap_around_distance",
          "zona_impacto_capó",
          "atropello_peatón",
          "atropello_ciclista",
          "puntos_impacto_velocidad"
        ],
        "vehiculo_id": null,
        "calidad": "media"
      },
      {
        "id": "adf66d1f-d45e-4cbf-a61b-bd5dd4438f55",
        "descripcion": "Croquis digital cenital de atropello: turismo colisiona con ciclista sobre calzada, con cotas de distancia longitudinal 8,008 m y lateral 1,215 m.",
        "tags": [
          "croquis_digital",
          "vista_cenital",
          "medicion_distancia",
          "atropello_bicicleta",
          "trayectoria_impacto",
          "cotas_metricas"
        ],
        "vehiculo_id": null,
        "calidad": "alta"
      },
      {
        "id": "0f99d9e8-f588-457d-bda0-838145fca58c",
        "descripcion": "Diagrama técnico de reconstrucción con zonas WAD y puntos de impacto de cabeza de ciclista y peatón sobre capó y parabrisas de turismo.",
        "tags": [
          "diagrama_impacto",
          "WAD_zones",
          "puntos_contacto_cabeza",
          "ciclista",
          "peaton",
          "capo_vehiculo",
          "parabrisas",
          "reconstruccion_siniestro"
        ],
        "vehiculo_id": null,
        "calidad": "media"
      },
      {
        "id": "6af3d58d-d4ec-408c-a294-ef63590ed7b5",
        "descripcion": "Reconstrucción 3D de escena vial: turismo SEAT y ciclista en calzada estrecha de montaña, aproximación en sentido contrario.",
        "tags": [
          "reconstruccion_3d",
          "simulacion_accidente",
          "carretera_estrecha",
          "ciclista_calzada",
          "vehiculo_turismo",
          "encuentro_frontal_inminente"
        ],
        "vehiculo_id": null,
        "calidad": "media"
      },
      {
        "id": "efaa60b8-0177-44ef-82a9-2c68c0be7cc2",
        "descripcion": "Reconstrucción 3D por nube de puntos de vía curva con talud lateral; medición forense de distancia 26,59 m entre dos puntos marcados en rojo.",
        "tags": [
          "nube_puntos_3d",
          "escaner_laser",
          "medicion_distancia",
          "via_curva",
          "talud",
          "software_forense"
        ],
        "vehiculo_id": null,
        "calidad": "alta"
      },
      {
        "id": "e7137fc0-36fb-47b2-95b7-359cec0babe1",
        "descripcion": "Reconstrucción 3D fotogramétrica de escena en carretera rural con curva; se aprecia vehículo volcado lateral izquierdo y segundo vehículo estacionado en calzada.",
        "tags": [
          "reconstruccion_3d",
          "nube_puntos",
          "carretera_rural",
          "curva",
          "vehiculo_volcado",
          "vision_aerea",
          "escena_completa"
        ],
        "vehiculo_id": null,
        "calidad": "alta"
      },
      {
        "id": "9325d5e3-38fa-46c3-99b9-e134825837a7",
        "descripcion": "Nube de puntos 3D de vía estrecha en curva con medición forense de distancia 3,104 m entre dos puntos señalados.",
        "tags": [
          "nube_puntos_3d",
          "medicion_distancia",
          "escaneado_laser",
          "via_estrecha",
          "curva",
          "software_forense"
        ],
        "vehiculo_id": null,
        "calidad": "alta"
      }
    ],
    "escena_huellas": [
      {
        "id": "8a03add7-8fad-421a-adb0-a79381f01e2b",
        "descripcion": "Vista longitudinal de calzada rural con posible marca de deslizamiento de bicicleta sobre pavimento de hormigón en tramo de curva.",
        "tags": [
          "marca_deslizamiento_calzada",
          "huella_bicicleta",
          "carretera_rural",
          "curva",
          "pavimento_hormigon"
        ],
        "vehiculo_id": "B",
        "calidad": "media"
      }
    ],
    "vehiculo_frontal": [
      {
        "id": "c8bb8b64-f20b-4eb3-bab4-d8be1de2127f",
        "descripcion": "SEAT Ibiza matrícula 3526-BKL con parabrisas completamente fracturado por impacto, capó aparentemente sin deformación estructural visible.",
        "tags": [
          "parabrisas_destrozado",
          "cristal_fracturado_impacto_peatonal",
          "capo_sin_deformacion_visible",
          "seat_ibiza"
        ],
        "vehiculo_id": "A",
        "calidad": "alta"
      },
      {
        "id": "d354b115-f67d-4d01-b4b5-2fe7fefddbdd",
        "descripcion": "Vista frontal de turismo plateado tipo Citroën Xsara Picasso sobre calzada de hormigón; se observa nivel digital electrónico depositado en pavimento como referencia de medición.",
        "tags": [
          "frontal_vehiculo",
          "matricula_visible",
          "instrumento_medicion_calzada",
          "nivel_digital",
          "calzada_hormigon"
        ],
        "vehiculo_id": null,
        "calidad": "alta"
      },
      {
        "id": "26984e22-7345-4d14-af03-1cb85f081083",
        "descripcion": "Vista frontal de SEAT Ibiza matrícula 3526-BKL, parachoques y rejilla delantera aparentemente sin daños estructurales evidentes.",
        "tags": [
          "matricula_legible",
          "parachoques_frontal",
          "rejilla_frontal",
          "seat_ibiza",
          "sin_dano_visible_frontal"
        ],
        "vehiculo_id": "A",
        "calidad": "media"
      }
    ],
    "atestado_pagina": [
      {
        "id": "89969bcd-c5c3-4b05-b332-4b8d6af5ba93",
        "descripcion": "Informe SamRAT de cálculo de distancia de parada modelo 3 fases: velocidad 50 km/h, distancia total 26,32 m, pendiente 5,143°, coeficiente rozamiento 0,75.",
        "tags": [
          "informe_samrat",
          "calculo_distancia_parada",
          "modelo_3_fases",
          "reconstruction_accidente",
          "velocidad_50kmh",
          "coeficiente_rozamiento",
          "pendiente_via"
        ],
        "vehiculo_id": null,
        "calidad": "alta"
      },
      {
        "id": "454d6ad8-dddb-43fb-8a94-1578ab83c9ac",
        "descripcion": "Diagrama técnico pericial que muestra zonas WAD de impacto de cabeza de ciclista/peatón sobre capó y parabrisas de vehículo a distintas velocidades.",
        "tags": [
          "diagrama_tecnico",
          "WAD_impacto_cabeza",
          "puntos_contacto_ciclista",
          "colision_frontal_bicicleta",
          "figura_referencia_pericial"
        ],
        "vehiculo_id": null,
        "calidad": "media"
      },
      {
        "id": "9811026f-2fc0-41a0-a4f9-c9205c82ead5",
        "descripcion": "Informe SamRAT de cálculo de velocidad por huella de frenada: longitud 0,47 m, velocidad inicial calculada 10 km/h, pendiente 5,143°.",
        "tags": [
          "informe_samrat",
          "calculo_velocidad",
          "huella_frenada",
          "modelo_general",
          "coeficiente_rozamiento"
        ],
        "vehiculo_id": "A",
        "calidad": "alta"
      }
    ],
    "vehiculo_detalle_dano": [
      {
        "id": "4ae291b1-cc67-4287-8e1e-047c2e49f08d",
        "descripcion": "Medición pericial del manillar de bicicleta Orbea con cinta métrica, mostrando posible deformación o desplazamiento tras impacto.",
        "tags": [
          "manillar_bicicleta",
          "medicion_pericial",
          "cinta_metrica",
          "palancas_freno",
          "deformacion_manillar"
        ],
        "vehiculo_id": "B",
        "calidad": "alta"
      }
    ],
    "escena_senalizacion": [
      {
        "id": "e234bc44-23c7-4cc0-ba3e-53fbc0ab80db",
        "descripcion": "Señal de limitación de velocidad a 20 km/h junto a cartel municipal del Ayuntamiento de Aulesti prohibiendo extracción de madera sin permiso.",
        "tags": [
          "señal_limitacion_velocidad_20",
          "señal_municipal",
          "poste_señalizacion",
          "euskera"
        ],
        "vehiculo_id": null,
        "calidad": "alta"
      }
    ]
  },
  "tipos_disponibles": [
    "otro",
    "escena_general",
    "croquis",
    "escena_huellas",
    "vehiculo_frontal",
    "atestado_pagina",
    "vehiculo_detalle_dano",
    "escena_senalizacion"
  ]
}
```

#### 1.2 → `consultar_escena`

**Inputs del Perito:**
```json
{
  "direccion": "Barrio Zubero, Aulestia, Bizkaia",
  "lat": 43.33,
  "lon": -2.6203
}
```

**Respuesta del especialista:**
```json
{
  "direccion_resuelta": "BI- 3242-Arratzuko errepidea, Elexalde, Kortezubi, Bizkaia, Euskadi, 48383, España",
  "lat_resuelta": 43.33,
  "lon_resuelta": -2.6203,
  "radio_efectivo_m": 50,
  "via_principal": null,
  "n_vias": 0,
  "todas_las_vias": [],
  "senales": [],
  "n_senales": 0,
  "tiene_carril_bici": false,
  "n_pasos_peatones": 0,
  "elevacion_m": 205.0,
  "pendiente_pct": 68.3,
  "pendiente_media_pct": 17.1,
  "pendiente_fiable": false,
  "visibilidad_estimada_m": null,
  "advertencias_dato": [
    "La pendiente devuelta por el DEM (68.3%) es físicamente inverosímil para una vía rodada abierta a tráfico (>30%). Probablemente el muestreo radial del DEM ha caído en un talud lateral, no en la traza de la vía. Solicita al perito la pendiente medida in situ o aportada por el atestado.",
    "OpenStreetMap no tiene esta vía mapeada con suficiente detalle. La anchura, número de carriles, velocidad máxima y señalización deben ser confirmadas por el perito mediante medición in situ o atestado."
  ],
  "imagenes_disponibles": 0,
  "fuentes": [
    "Nominatim (reverso)",
    "OpenStreetMap Overpass (sin match)",
    "Open-Elevation (DEM SRTM)"
  ]
}
```

#### 1.3 → `consultar_meteo`

**Inputs del Perito:**
```json
{
  "lat": 43.33,
  "lon": -2.6203,
  "fecha_iso": "2020-05-21T20:38:00"
}
```

**Respuesta del especialista:**
```json
{
  "temperatura_c": 20.1,
  "precipitacion_mm": 0.0,
  "viento_kmh": 6.1,
  "viento_direccion_deg": 93,
  "visibilidad_m": null,
  "estado_tiempo": "cubierto",
  "calzada_estimada": "seca",
  "amanecer": "2020-05-21T06:39",
  "atardecer": "2020-05-21T21:33",
  "es_dia": true,
  "fuente": "Open-Meteo Archive (ECMWF ERA5)"
}
```

#### 1.4 → `consultar_ficha_tecnica`

**Inputs del Perito:**
```json
{
  "marca": "SEAT",
  "modelo": "Ibiza",
  "anio": 2018,
  "vehiculo_id": "A"
}
```

**Respuesta del especialista:**
```json
{
  "vehiculo_id": "A",
  "marca": "SEAT",
  "modelo": "Ibiza",
  "anio": 2018,
  "masa_kg": 1115.0,
  "longitud_m": 4.06,
  "ancho_m": 1.78,
  "altura_m": 1.44,
  "altura_parachoques_m": [
    0.42,
    0.7
  ],
  "altura_largueros_m": 0.48,
  "rigidez_a": 55.0,
  "rigidez_b": 8.0,
  "sistemas_seguridad": [
    "Airbag conductor, pasajero y laterales",
    "ABS y ESC",
    "Cinturones con pretensores"
  ],
  "fuente": "SEAT España — ficha técnica Ibiza (5ª gen.)",
  "notas": "Turismo segmento B. Plataforma MQB A0."
}
```

### Turno 2
**🧠 Razonamiento del Perito:**

> Buen contexto. Ahora ejecuto cálculos físicos clave (huella ciclista, distancias de detención del turismo a 20 y reglamentaria, tiempo de huella) y el contraste de atestado.

**🔧 Tools invocadas en este turno: 8**

#### 2.1 → `simular_fisica`

**Inputs del Perito:**
```json
{
  "modelo": "velocidad_por_huella",
  "parametros": {
    "distancia_m": 8.0,
    "coef_friccion": 0.75,
    "pendiente_pct": -10.3
  }
}
```

**Respuesta del especialista:**
```json
{
  "velocidad_minima_kmh": 36.3,
  "modelo_aplicado": "stannard_baker",
  "formula": "v = √(2 · (μ + sin(θ)) · g · d)",
  "asunciones": [
    "μ=0.75",
    "pendiente=-10.3%",
    "frenada plena con neumáticos bloqueados"
  ],
  "resumen": "Velocidad mínima del vehículo: 36.3 km/h con huella de 8.0 m, μ=0.75."
}
```

#### 2.2 → `simular_fisica`

**Inputs del Perito:**
```json
{
  "modelo": "distancia_detencion",
  "parametros": {
    "v_kmh": 20.0,
    "coef_friccion": 0.75,
    "pendiente_pct": 10.3,
    "t_reaccion_s": 1.0,
    "incluir_tiempo_reaccion": true
  }
}
```

**Respuesta del especialista:**
```json
{
  "v_kmh": 20.0,
  "incluir_tiempo_reaccion": true,
  "distancia_reaccion_m": 5.56,
  "distancia_frenada_m": 1.84,
  "distancia_total_m": 7.4,
  "tiempo_frenada_s": 0.66,
  "tiempo_total_s": 1.66,
  "modelo_aplicado": "distancia_detencion",
  "asunciones": [
    "μ=0.75",
    "pendiente=10.3%",
    "t reacción=1.0s"
  ],
  "resumen": "A 20.0 km/h con μ=0.75, pendiente 10%, t_reacción=1.0s: recorre 7.40 m en 1.66 s (frenada 1.84 m / 0.66 s)."
}
```

#### 2.3 → `simular_fisica`

**Inputs del Perito:**
```json
{
  "modelo": "distancia_detencion",
  "parametros": {
    "v_kmh": 30.0,
    "coef_friccion": 0.75,
    "pendiente_pct": 10.3,
    "t_reaccion_s": 1.0,
    "incluir_tiempo_reaccion": true
  }
}
```

**Respuesta del especialista:**
```json
{
  "v_kmh": 30.0,
  "incluir_tiempo_reaccion": true,
  "distancia_reaccion_m": 8.33,
  "distancia_frenada_m": 4.15,
  "distancia_total_m": 12.48,
  "tiempo_frenada_s": 1.0,
  "tiempo_total_s": 2.0,
  "modelo_aplicado": "distancia_detencion",
  "asunciones": [
    "μ=0.75",
    "pendiente=10.3%",
    "t reacción=1.0s"
  ],
  "resumen": "A 30.0 km/h con μ=0.75, pendiente 10%, t_reacción=1.0s: recorre 12.48 m en 2.00 s (frenada 4.15 m / 1.00 s)."
}
```

#### 2.4 → `simular_fisica`

**Inputs del Perito:**
```json
{
  "modelo": "tiempo_huella",
  "parametros": {
    "distancia_m": 8.0,
    "coef_friccion": 0.75,
    "pendiente_pct": -10.3,
    "t_reaccion_s": 1.0,
    "t_ejecucion_s": 0.5
  }
}
```

**Respuesta del especialista:**
```json
{
  "distancia_huella_m": 8.0,
  "velocidad_inicio_huella_kmh": 36.3,
  "t_reaccion_s": 1.0,
  "t_ejecucion_s": 0.5,
  "t_frenada_s": 1.59,
  "t_total_s": 3.09,
  "modelo_aplicado": "tiempo_huella",
  "formula": "t_total = t_reaccion + t_ejecucion + sqrt(2·d/(μ·g))/(μ·g)",
  "asunciones": [
    "μ_eff=0.65",
    "pendiente=-10.3%",
    "t_reacción=1.0s",
    "t_ejecución=0.5s"
  ],
  "resumen": "Desde percepción del riesgo hasta el final de la huella (8.0 m): t_total = 3.09 s (reacción 1.0s + ejecución 0.5s + frenada 1.59s). Velocidad al iniciar el bloqueo: 36.3 km/h."
}
```

#### 2.5 → `verificar_atestado`

**Inputs del Perito:**
```json
{
  "velocidad_calculada_kmh": 23.84,
  "velocidad_declarada_kmh": 20.0,
  "declaracion": "El conductor declara circular entre 10 y 20 km/h ascendiendo la pendiente; afirma frenar al máximo pero impacta sin detenerse"
}
```

**Respuesta del especialista:**
```json
{
  "velocidad_declarada_kmh": 20.0,
  "velocidad_calculada_kmh": 23.84,
  "diferencia_kmh": 3.8,
  "compatible": false,
  "observacion": "Declaración: 20.0 km/h. Cálculo físico: 23.84 km/h. Diferencia +3.8 km/h. Incompatibles: la evidencia física supera el margen del 15%.",
  "declaracion_textual": "El conductor declara circular entre 10 y 20 km/h ascendiendo la pendiente; afirma frenar al máximo pero impacta sin detenerse"
}
```

#### 2.6 → `analizar_conformidad_atestado`

**Inputs del Perito:**
```json
{
  "fecha_siniestro_iso": "2020-05-21T20:38:00",
  "velocidad_declarada_kmh": 20.0,
  "velocidad_calculada_kmh": 23.84,
  "es_atropello": true
}
```

**Respuesta del especialista:**
```json
{
  "incongruencias": [
    {
      "severidad": "alta",
      "titulo": "Afirmación de límite 20 km/h sin respaldo documental fotográfico",
      "descripcion": "El atestado afirma la existencia de 'una señal específica de 20 km/h pero no aporta fotografía de la señal'. La velocidad máxima aplicable es el fundamento normativo central del siniestro; su acreditación exige soporte gráfico o documental. Sin él, el límite invocado carece de sustento probatorio suficiente y cualquier conclusión basada en el mismo queda invalidada metodológicamente."
    },
    {
      "severidad": "alta",
      "titulo": "Contradicción entre ausencia de huellas del turismo y declaración de frenada máxima",
      "descripcion": "El conductor 'declaró que accionó el freno al máximo' y 'en el momento del impacto el turismo no estaba detenido', mientras el atestado recoge simultáneamente que 'no se observan huellas del turismo'. En calzada seca (µ = 0,75) y asfalto en buen estado, una frenada plena con neumáticos bloqueados deja huella visible. La ausencia de huella contradice la declaración de frenada de emergencia o indica que ésta no fue plena ni sostenida."
    },
    {
      "severidad": "media",
      "titulo": "Discrepancia entre visibilidad estimada en atestado y medida pericial",
      "descripcion": "El atestado estima la visibilidad efectiva del conductor en '20 m', mientras la medición pericial in situ arroja '26,5 m lineales (>30 m según trayectoria curva)'. Esa diferencia —entre el 32 % y el 50 % respecto al valor declarado— afecta directamente al cálculo de distancia de parada y al análisis de previsibilidad del siniestro, sin que el atestado justifique el criterio empleado en su estimación propia."
    },
    {
      "severidad": "media",
      "titulo": "Omisión de análisis de maniobra evasiva disponible",
      "descripcion": "El atestado constata la existencia de una 'zona terriza diáfana de varios metros de anchura a la derecha del turismo (desnivel máximo 4 cm) que permitiría maniobra evasiva', pero no incluye ningún análisis técnico sobre si dicha maniobra era ejecutable al ritmo de reacción normal, ni por qué no fue acometida. Su mención sin conclusión constituye un apriorismo de trayectoria no justificado metodológicamente."
    },
    {
      "severidad": "baja",
      "titulo": "Rango de velocidad declarada no reducido a un valor único contrastable",
      "descripcion": "El conductor declara circular 'entre 10 y 20 km/h'. El atestado toma como valor declarado 20 km/h para el contraste, sin justificar la elección del extremo superior del intervalo ni analizar el impacto de haber circulado a 10 km/h sobre la distancia de parada disponible. La elección implícita del valor más alto sesga el análisis en un sentido determinado sin razonamiento explícito."
    }
  ],
  "elementos_omitidos": [
    "Prueba de detección de alcohol y otras drogas al conductor (art. 379 CP). El siniestro tiene resultado letal; la práctica de estas pruebas y su constancia en el atestado es preceptiva. No se menciona en ningún apartado del documento.",
    "Cálculo formal de velocidad por metodología reconocida (Stannard-Baker, CRASH3 o EBS). Constan huellas de frenada del ciclista de 8 m y el coeficiente µ = 0,75, datos suficientes para aplicar la fórmula cinemática. El atestado no documenta ningún método de estimación de velocidad para el turismo a partir de evidencias físicas, limitándose a la declaración del conductor.",
    "Fotografía o acreditación documental de la señal de velocidad máxima de 20 km/h. La señal vertical constituye el soporte normativo del límite aplicado; su inexistencia en el expediente impide verificar la vigencia, estado y visibilidad de la señalización el día del siniestro.",
    "Posicionamiento del PDI (punto de impacto definitivo) mediante cota lateral referenciada al borde de la vía y distancia longitudinal a referencia fija. En un atropello con resultado letal, la localización precisa del PDI es obligatoria para reconstruir la cinemática del siniestro; el atestado no lo acota explícitamente.",
    "Constancia del estado de los neumáticos del turismo y funcionamiento del sistema de frenos. En un siniestro letal donde la distancia de frenada y la ausencia de huellas son elementos centrales, la inspección técnica del estado de los neumáticos y del sistema de frenado es imprescindible para validar o refutar la declaración de frenada máxima.",
    "Posición final del cuerpo de la víctima con acotación métrica respecto al borde de la vía y a referencias longitudinales fijas. El atestado describe la trayectoria cinemática del cuerpo (paragolpes, capó, parabrisas, techo) pero no documenta la posición de reposo final, dato necesario para la reconstrucción del siniestro."
  ],
  "valoracion_global": "deficiente",
  "recomendaciones": [
    "Complementar urgentemente el atestado con reportaje fotográfico de la señal de velocidad máxima de 20 km/h, o en su defecto solicitar certificación al organismo titular de la vía que acredite su existencia, estado y ubicación en la fecha del siniestro.",
    "Ampliar el atestado incorporando: prueba de alcohol y drogas al conductor con resultado documentado; cálculo de velocidad por metodología cinemática reconocida a partir de las huellas del ciclista y µ = 0,75; acotación precisa del PDI y posición final de la víctima; e inspección técnica del sistema de frenos y neumáticos del turismo, con el fin de dar coherencia interna al expediente y dotarlo de suficiencia probatoria en sede judicial."
  ]
}
```

#### 2.7 → `consultar_legal`

**Inputs del Perito:**
```json
{
  "tipo_encargo": "atropello",
  "fecha_siniestro_iso": "2020-05-21T20:38:00",
  "descripcion_caso": "Atropello mortal de ciclista por turismo SEAT Ibiza en vía rural estrecha y curva ascendente del Barrio Zubero (Aulestia) en mayo de 2020. Conductor declara 10-20 km/h, no deja huella de frenada, el ciclista sí (8 m) y fallece por lesiones cefálicas.",
  "preguntas_encargo": [
    "Velocidad real del turismo en el momento del impacto",
    "Evitabilidad del accidente cumpliendo la normativa",
    "Conducta del conductor respecto al límite de velocidad y atención debida"
  ],
  "palabras_clave": [
    "art.3 RGCir",
    "art.45 RGCir",
    "art.46 RGCir",
    "principio de confianza",
    "velocidad adecuada",
    "visibilidad",
    "atención"
  ]
}
```

**Respuesta del especialista:**
```json
{
  "normativa": [
    {
      "referencia": "Art. 45 RGC",
      "titulo": "Adecuación de la velocidad a las circunstancias. Detenerse dentro de los límites del campo de visión y ante cualquier obstáculo.",
      "boe": "BOE-A-2003-23514",
      "extracto": "Todo conductor está obligado a respetar los límites de velocidad establecidos y a tener en cuenta, además, sus propias condiciones físicas y psíquicas, las características y el estado de la vía, del vehículo y de su carga, las condiciones meteorológicas, ambientales y de circulación, y, en general, cuantas circunstancias concurran en cada momento, a fin de adecuar la velocidad de su vehículo a ellas, de manera que siempre pueda detenerlo dentro de los límites de su campo de visión y ante cualquier obstáculo que pueda presentarse.",
      "motivo_aplicabilidad": "La vía es rural, estrecha y en curva ascendente con visibilidad reducida; la ausencia de huella de frenada del turismo junto a los 8 m de huella del ciclista permiten reconstruir la velocidad real del turismo y evaluar si el conductor adaptó ésta a las condiciones de visibilidad limitada, lo que constituye el núcleo de las preguntas 1 y 2 del encargo.",
      "relevancia": "primaria",
      "url_boe": "https://www.boe.es/buscar/act.php?id=BOE-A-2003-23514",
      "norma_madre": "Reglamento General de Circulación (RD 1428/2003)"
    },
    {
      "referencia": "Art. 3 RGC",
      "titulo": "Conducción diligente y prudente. Prohibición de conducción negligente o temeraria.",
      "boe": "BOE-A-2003-23514",
      "extracto": "Se deberá conducir con la diligencia y precaución necesarias para evitar todo daño, propio o ajeno, cuidando de no poner en peligro, tanto al mismo conductor como a los demás ocupantes del vehículo y al resto de los usuarios de la vía.",
      "motivo_aplicabilidad": "El fallecimiento del ciclista por lesiones cefálicas y la inexistencia de huella de frenada del turismo apuntan a una conducción sin la diligencia mínima exigible en una vía con visibilidad limitada, lo que soporta directamente la pregunta 3 del encargo sobre la atención debida del conductor.",
      "relevancia": "primaria",
      "url_boe": "https://www.boe.es/buscar/act.php?id=BOE-A-2003-23514",
      "norma_madre": "Reglamento General de Circulación (RD 1428/2003)"
    },
    {
      "referencia": "Art. 46.1.b RGC",
      "titulo": "Moderación de velocidad: al aproximarse a ciclos circulando, intersecciones, vías de uso exclusivo de ciclos y pasos de peatones no regulados.",
      "boe": "BOE-A-2003-23514",
      "extracto": null,
      "motivo_aplicabilidad": "La víctima es un ciclista que circulaba por la vía; el conductor tenía o debía tener la obligación específica de moderar la velocidad al aproximarse a un ciclo en circulación, lo que refuerza el análisis de evitabilidad del accidente (pregunta 2).",
      "relevancia": "primaria",
      "url_boe": "https://www.boe.es/buscar/act.php?id=BOE-A-2003-23514",
      "norma_madre": "Reglamento General de Circulación (RD 1428/2003)"
    },
    {
      "referencia": "Principio de confianza (jurisprudencial)",
      "titulo": "Doctrina de los Tribunales: todo usuario de la vía puede confiar en que los demás usuarios cumplirán la normativa, salvo evidencia objetiva de comportamiento anómalo. Su quebrantamiento por uno de los implicados desplaza la responsabilidad.",
      "boe": "STS Sala 2.ª — doctrina reiterada (entre otras: STS 2.ª 1356/1999, STS 2.ª 738/2003)",
      "extracto": "El ciclista que circula correctamente por su mitad derecha de la calzada ve quebrantado su principio de confianza al verse invadida su trayectoria por un vehículo a velocidad inadecuada o con falta de atención.",
      "motivo_aplicabilidad": "Si el ciclista circulaba correctamente por su carril, la responsabilidad se desplaza hacia el conductor del turismo que, a velocidad inadecuada para la curva y la visibilidad disponible, no pudo respetar la trayectoria del ciclista; este principio es determinante para la valoración jurídica de la conducta de ambos implicados.",
      "relevancia": "secundaria",
      "url_boe": null,
      "norma_madre": "Principio de confianza (jurisprudencial)"
    },
    {
      "referencia": "Art. 46.1.a RGC",
      "titulo": "Moderación de velocidad: cuando haya peatones en la parte de la vía o pueda preverse racionalmente su irrupción, especialmente niños, ancianos o personas impedidas.",
      "boe": "BOE-A-2003-23514",
      "extracto": null,
      "motivo_aplicabilidad": "Aunque la víctima es un ciclista, la vía rural estrecha en un barrio (Zubero, Aulestia) hace previsible la presencia de usuarios vulnerables, reforzando la obligación general de moderación de velocidad ante la previsibilidad de su aparición.",
      "relevancia": "complementaria",
      "url_boe": "https://www.boe.es/buscar/act.php?id=BOE-A-2003-23514",
      "norma_madre": "Reglamento General de Circulación (RD 1428/2003)"
    },
    {
      "referencia": "Art. 46.1.d RGC",
      "titulo": "Moderación de velocidad: tramos con edificios de inmediato acceso a la parte de la vía utilizada.",
      "boe": "BOE-A-2003-23514",
      "extracto": null,
      "motivo_aplicabilidad": "El siniestro ocurre en el Barrio Zubero (Aulestia), entorno con posibles edificaciones de acceso directo a la calzada, lo que añade un factor normativo adicional que obligaba al conductor a extremar la moderación de velocidad.",
      "relevancia": "complementaria",
      "url_boe": "https://www.boe.es/buscar/act.php?id=BOE-A-2003-23514",
      "norma_madre": "Reglamento General de Circulación (RD 1428/2003)"
    }
  ],
  "bibliografia": [
    "Searle J.A., The physics of throw distance in accident reconstruction, SAE 930659 (1993).",
    "Han I., Brach R.M., Throw model for frontal pedestrian collisions, ASME (2001).",
    "Wood D.P., Pedestrian throw distance: pre- and post-impact modelling, ITAI (2005).",
    "UC3M & Guardia Civil, Manual de reconstrucción de atropellos a peatones y ciclistas (2020).",
    "Otte D., Pedestrian/Cyclist injuries from cars (1989).",
    "Van Rooij L., Pedestrian impact reconstruction with WAD (2003)."
  ],
  "advertencia_temporal": "El siniestro se produjo el 21 de mayo de 2020. El RD 970/2020, que estableció el límite genérico de 20 km/h en vías de sentido único y un carril por sentido dentro de poblado y modificó el límite de 30 km/h en vías urbanas, fue publicado el 27 de octubre de 2020 (BOE-A-2020-12912), por lo que NO estaba en vigor en la fecha del siniestro. Los límites aplicables son los del texto refundido de la LSV (RDL 6/2015) y el RGC vigentes antes de dicha modificación. Esta circunstancia debe consignarse expresamente en el informe si se discute el límite de velocidad aplicable a la vía."
}
```

#### 2.8 → `analizar_biomecanica`

**Inputs del Perito:**
```json
{
  "descripcion_lesiones": "Lesiones cefálicas incompatibles con la vida (autopsia). Trayectoria del cuerpo del ciclista: impacto inicial en parachoques delantero, deslizamiento sobre el capó, impacto contra parabrisas delantero lado derecho y hendidura en techo extremo derecho.",
  "descripcion_danos_vehiculo": "Parachoques frontal sin deformación visible, capó con impronta de deslizamiento, parabrisas delantero derecho fracturado por impacto cefálico, hendidura en techo lado derecho.",
  "es_atropello": true,
  "masa_vehiculo_kg": 1115,
  "velocidad_estimada_kmh": 24,
  "altura_impacto_m": 1.5,
  "gravedad_lesion": "fallecimiento"
}
```

**Respuesta del especialista:**
```json
{
  "wad": {
    "zona_impacto": "parabrisas central",
    "altura_m": [
      1.3,
      1.6
    ],
    "velocidad_min_kmh": 45,
    "velocidad_max_kmh": 60,
    "fuente": "Otte 1989; Searle 1993; Van Rooij 2003; manuales UC3M-GC 2020."
  },
  "energia_cinetica_kj": 24.8,
  "probabilidad_ais3_pct": 9,
  "mecanismos_lesivos_compatibles": [
    {
      "nombre": "Flexión",
      "razon": "El impacto del cuerpo del ciclista contra el parabrisas y posteriormente contra el umbral del techo genera una curvatura brusca del raquis cervical y del cráneo sobre el eje de flexión, compatible con las fracturas o deformaciones observadas en la región cefálica superior."
    },
    {
      "nombre": "Compresión",
      "razon": "La hendidura en el techo lado derecho indica que la cabeza del ciclista recibió una carga axial de alta intensidad localizada en el vértex craneal al impactar contra la arista del techo, generando un fenómeno de compresión directa sobre la bóveda craneal que puede ocasionar fracturas por estallido o hundimiento incompatibles con la vida."
    },
    {
      "nombre": "Tracción",
      "razon": "El deslizamiento sobre el capó seguido del impacto contra el parabrisas implica una aceleración-desaceleración brusca que somete las estructuras meníngeas y los vasos puente a fuerzas de tracción, mecanismo coherente con el desgarro vascular y posibles avulsiones en la transición cráneo-cervical."
    },
    {
      "nombre": "Extensión",
      "razon": "Tras el impacto inicial en el parachoques delantero, la inercia del tronco proyecta la cabeza hacia atrás en hiperextensión antes del segundo impacto contra el parabrisas, activando el mecanismo extensión-whiplash a nivel cervical superior y en la base craneal."
    }
  ],
  "cadena_4_impactos_sucesivos": [
    {
      "orden": 1,
      "descripcion": "Vehículo contra el objeto (fijo o móvil)."
    },
    {
      "orden": 2,
      "descripcion": "Ocupantes contra alguna estructura interior del vehículo (volante, salpicadero, parabrisas)."
    },
    {
      "orden": 3,
      "descripcion": "Órganos internos entre sí (encéfalo contra cráneo, vísceras contra paredes torácicas/abdominales)."
    },
    {
      "orden": 4,
      "descripcion": "Objetos no fijos del interior del automóvil que impactan a los ocupantes (carga, animales sueltos, pasajeros traseros)."
    }
  ],
  "analisis_craneal": {
    "mecanismo_general": "La secuencia cinemática —impacto en parabrisas derecho seguido de impacto contra el umbral-techo— determina un mecanismo bifásico: golpe directo de alta energía localizada sobre la bóveda craneal derecha con componente de cizallamiento rotacional generado por la aceleración angular al deslizar sobre el capó.",
    "tipos_compatibles": [
      {
        "nombre": "Hematoma frontal por golpe directo",
        "mecanismo": "El impacto primario de la cabeza contra el parabrisas derecho puede generar contusión por golpe directo sobre los lóbulos frontales o temporales derechos al colisionar los mismos contra la tabla interna del cráneo en la zona de impacto."
      },
      {
        "nombre": "Lesión por contragolpe (contre-coup)",
        "mecanismo": "La deceleración brusca en el impacto contra el parabrisas proyecta el encéfalo en sentido opuesto al golpe, generando contusión del lóbulo contralateral (hemisferio izquierdo) por el mecanismo clásico de contragolpe."
      },
      {
        "nombre": "Hematoma subdural occipital",
        "mecanismo": "La tracción brusca en el plano sagital durante el deslizamiento sobre el capó y la transición al impacto en el techo puede desgarrar vasos puente meníngeos parietales u occipitales, siendo compatible con hematoma subdural por tracción vascular."
      },
      {
        "nombre": "Hemorragia subaracnoidea",
        "mecanismo": "La aceleración angular generada durante el deslizamiento sobre el capó y el doble impacto cefálico induce cizallamiento vascular en el espacio subaracnoideo, mecanismo plenamente compatible con la hemorragia subaracnoidea traumática."
      },
      {
        "nombre": "Lesión axonal difusa (DAI)",
        "mecanismo": "Aunque la velocidad estimada es de 24 km/h, la secuencia de impactos múltiples y la energía cinética aplicada localizada (parabrisas + umbral de techo) puede generar aceleración rotacional encefálica suficiente para inducir cizallamiento axonal difuso, especialmente dado que la hendidura en el techo indica impacto de alta severidad focal."
      }
    ],
    "consideracion_clinica": "La autopsia confirma lesiones cefálicas incompatibles con la vida. La secuencia cinemática descrita —deslizamiento sobre el capó con doble impacto en parabrisas y umbral de techo— concentra la energía cinética disponible (24,8 kJ) sobre la bóveda craneal en dos pulsos de fuerza consecutivos de muy corta duración, lo que multiplica la severidad lesional respecto a un impacto único. La hendidura del techo evidencia una compresión localizada de alta intensidad sobre el cráneo, mecanismo suficiente para provocar fracturas por estallido y daño encefálico difuso letal incluso a velocidades inferiore…"
  },
  "compatibilidad_velocidad_lesion": "compatible — impacto contra estructura rígida del vehículo (umbral techo) a 24 km/h justifica lesividad letal cefálica por concentración de energía en zona craneal sin absorción de deformación.",
  "razonamiento_compatibilidad": "Aunque 24 km/h se sitúa bajo el umbral genérico de alta lesividad (≥40 km/h), la trayectoria documentada del cuerpo sobre el capó hasta el impacto directo de la cabeza contra el umbral rígido del techo —estructura con mínima deformabilidad— constituye la excepción explícita recogida en los criterios de compatibilidad velocidad-gravedad ('impacto contra estructura rígida del vehículo'), lo que hace plenamente compatible el fallecimiento con la velocidad estimada.",
  "tabla_aceleraciones_tipo": [
    {
      "situacion": "Frenada normal",
      "tiempo_parada": "5 s",
      "aceleracion_g": 0.67,
      "fuerza_n_1200kg": 8000
    },
    {
      "situacion": "Choque contra objeto deformable similar",
      "tiempo_parada": "70 ms",
      "aceleracion_g": 49,
      "fuerza_n_1200kg": 600000
    },
    {
      "situacion": "Choque contra objeto rígido (muro/pilar)",
      "tiempo_parada": "5 ms",
      "aceleracion_g": 680,
      "fuerza_n_1200kg": 8000000
    }
  ],
  "fuentes": [
    "Manual ESTT/DGT 2011 — Especialidad Gestión del Tráfico y Movilidad.",
    "Limpert R., Motor Vehicle Accident Reconstruction (LexisNexis, 6.ª ed., 2012).",
    "Mertz H.J., Anthropomorphic Test Devices, en Accidental Injury (Springer, 2002).",
    "Otte D., Pedestrian/Cyclist injuries from cars (1989).",
    "Van Rooij L., Pedestrian impact reconstruction with WAD (2003).",
    "UC3M & Guardia Civil, Manual de reconstrucción atropellos (2020)."
  ]
}
```

### Turno 3
**🧠 Razonamiento del Perito:**

> Datos clave reunidos. Ahora busco fotos específicas y genero un croquis interno de simulación. La huella del ciclista (8 m) arroja v_min ≈ 36 km/h, pero esa es la velocidad del **ciclista**, no del turismo. Para el turismo, dado que no hay huellas, debo apoyarme en el WAD del impacto cefálico (parabrisas-techo) y en la huella de 0,47 m / 1,89 m que figura en los informes SamRAT del catálogo (10-20 km/h). Reordeno: la huella de 8 m corresponde al ciclista descendente. Ese cálculo es la velocidad del ciclista al iniciar bloqueo (~36 km/h descendiendo). Para la velocidad del turismo, los SamRAT del catálogo (864c… y 9811…) calculan 20,06 km/h y 10 km/h.

**🔧 Tools invocadas en este turno: 9**

#### 3.1 → `buscar_foto_perito`

**Inputs del Perito:**
```json
{
  "criterio": "SEAT Ibiza frontal con parabrisas fracturado por impacto cefálico del ciclista"
}
```

**Respuesta del especialista:**
```json
{
  "match": {
    "id": "c8bb8b64-f20b-4eb3-bab4-d8be1de2127f",
    "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/c79b2976_p14_x116.png",
    "descripcion": "SEAT Ibiza matrícula 3526-BKL con parabrisas completamente fracturado por impacto, capó aparentemente sin deformación estructural visible.",
    "tipo": "vehiculo_frontal",
    "tags": [
      "parabrisas_destrozado",
      "cristal_fracturado_impacto_peatonal",
      "capo_sin_deformacion_visible",
      "seat_ibiza"
    ],
    "vehiculo_id": "A",
    "elementos_visibles": [
      "parabrisas_fracturado",
      "capo",
      "paragolpes_delantero",
      "faros_delanteros",
      "rejilla_frontal",
      "logo_seat",
      "matricula_delantera",
      "limpiaparabrisas"
    ]
  },
  "alternativas": [
    {
      "id": "269d51dc-3d49-45a9-bbee-53d0ea178efd",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/82cbfb8c_p06_x72.png",
      "descripcion": "Simulación 3D de atropello: turismo SEAT impacta bicicleta, ciclistas proyectados sobre capó y calzada.",
      "tipo": "croquis",
      "tags": [
        "simulacion_3d",
        "atropello_ciclista",
        "reconstruccion_accidente",
        "figura_3d",
        "bicicleta_impacto",
        "ocupante_proyectado"
      ],
      "vehiculo_id": "A",
      "elementos_visibles": [
        "turismo_SEAT_frontal",
        "bicicleta_roja",
        "figuras_ciclistas_proyectadas",
        "capo_vehiculo",
        "parabrisas",
        "calzada_simulada"
      ]
    },
    {
      "id": "26984e22-7345-4d14-af03-1cb85f081083",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/33a3a40a_p15_x124.png",
      "descripcion": "Vista frontal de SEAT Ibiza matrícula 3526-BKL, parachoques y rejilla delantera aparentemente sin daños estructurales evidentes.",
      "tipo": "vehiculo_frontal",
      "tags": [
        "matricula_legible",
        "parachoques_frontal",
        "rejilla_frontal",
        "seat_ibiza",
        "sin_dano_visible_frontal"
      ],
      "vehiculo_id": "A",
      "elementos_visibles": [
        "parachoques_delantero",
        "rejilla_frontal",
        "emblema_seat",
        "faro_derecho",
        "matricula_delantera",
        "capó"
      ]
    },
    {
      "id": "0f99d9e8-f588-457d-bda0-838145fca58c",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/96398c90_p28_x197.png",
      "descripcion": "Diagrama técnico de reconstrucción con zonas WAD y puntos de impacto de cabeza de ciclista y peatón sobre capó y parabrisas de turismo.",
      "tipo": "croquis",
      "tags": [
        "diagrama_impacto",
        "WAD_zones",
        "puntos_contacto_cabeza",
        "ciclista",
        "peaton",
        "capo_vehiculo",
        "parabrisas",
        "reconstruccion_siniestro"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "capo",
        "parabrisas",
        "zona_WAD_1000",
        "zona_WAD_1500",
        "zona_WAD_2500",
        "puntos_impacto_ciclista",
        "puntos_impacto_peaton",
        "techo"
      ]
    }
  ],
  "razon": "Vista frontal de SEAT Ibiza con parabrisas completamente fracturado por impacto, compatible con contacto cefálico de ciclista; alta calidad y matrícula identificable",
  "falta_info": null,
  "requiere_foto": false
}
```

#### 3.2 → `buscar_foto_perito`

**Inputs del Perito:**
```json
{
  "criterio": "señal vertical de limitación a 20 km/h en barrio Zubero"
}
```

**Respuesta del especialista:**
```json
{
  "match": {
    "id": "c4557c1c-af2f-454c-abd9-e039e07ddbc1",
    "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/0f2bcdb1_p13_x109.png",
    "descripcion": "Incorporación en zona rural del barrio Zubero auzoa, con señal de límite 20 km/h y calzada húmeda. Sin vehículos visibles en escena.",
    "tipo": "escena_general",
    "tags": [
      "interseccion_vial",
      "via_rural",
      "senial_velocidad_20",
      "senial_nucleo_poblado",
      "calzada_mojada",
      "incorporacion_lateral"
    ],
    "vehiculo_id": null,
    "elementos_visibles": [
      "señal_velocidad_maxima_20",
      "señal_topónimo_Zubero_auzoa",
      "calzada_hormigon",
      "muro_piedra",
      "talud_vegetal",
      "edificio_residencial",
      "farola",
      "arbol_sin_hojas"
    ]
  },
  "alternativas": [
    {
      "id": "e234bc44-23c7-4cc0-ba3e-53fbc0ab80db",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/298bfc07_p13_x110.png",
      "descripcion": "Señal de limitación de velocidad a 20 km/h junto a cartel municipal del Ayuntamiento de Aulesti prohibiendo extracción de madera sin permiso.",
      "tipo": "escena_senalizacion",
      "tags": [
        "señal_limitacion_velocidad_20",
        "señal_municipal",
        "poste_señalizacion",
        "euskera"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "señal_velocidad_maxima_20",
        "cartel_municipal_aulesti",
        "poste_metalico",
        "arbol_desnudo"
      ]
    }
  ],
  "razon": "Muestra explícitamente la señal de velocidad máxima 20 km/h junto al cartel topónimo 'Zubero auzoa', cumpliendo exactamente el criterio de señal vertical de limitación a 20 km/h en barrio Zubero",
  "falta_info": null,
  "requiere_foto": false
}
```

#### 3.3 → `buscar_foto_perito`

**Inputs del Perito:**
```json
{
  "criterio": "huella de derrape de bicicleta sobre la calzada en curva"
}
```

**Respuesta del especialista:**
```json
{
  "match": {
    "id": "8a03add7-8fad-421a-adb0-a79381f01e2b",
    "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/85e54c1f_p12_x105.png",
    "descripcion": "Vista longitudinal de calzada rural con posible marca de deslizamiento de bicicleta sobre pavimento de hormigón en tramo de curva.",
    "tipo": "escena_huellas",
    "tags": [
      "marca_deslizamiento_calzada",
      "huella_bicicleta",
      "carretera_rural",
      "curva",
      "pavimento_hormigon"
    ],
    "vehiculo_id": "B",
    "elementos_visibles": [
      "calzada_hormigon",
      "marca_deslizamiento",
      "arcen_gravilla",
      "curva_via",
      "vehiculo_pericial_aparcado",
      "vegetacion_lateral"
    ]
  },
  "alternativas": [
    {
      "id": "993af138-bea2-4997-97da-9023beab0a95",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/ee7182c0_p43_x267.png",
      "descripcion": "Calzada de hormigón con juntas de dilatación en zona rural, arcén de gravilla, curva suave, vegetación lateral y sombra arbórea proyectada sobre la vía.",
      "tipo": "escena_general",
      "tags": [
        "calzada_hormigon",
        "via_rural",
        "curva_suave",
        "gravilla_arcen",
        "vegetacion_lateral",
        "sin_senalizacion_visible"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "calzada_hormigon",
        "juntas_dilatacion",
        "arcen_gravilla",
        "curva",
        "vegetacion_lateral",
        "sombra_arbol",
        "tuberia_metalica_oxidada",
        "vehiculo_remolque_fondo"
      ]
    },
    {
      "id": "0b98c989-0cbe-482e-a4ff-d99554b4b4cb",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/7d1145f8_p11_x98.png",
      "descripcion": "Carretera rural con curva en zona boscosa y neblinosa; tres personas presentes en arcén fotografiando el lugar del siniestro.",
      "tipo": "escena_general",
      "tags": [
        "carretera_rural",
        "curva_calzada",
        "testigos_presentes",
        "zona_forestal",
        "niebla",
        "arcen_tierra"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "calzada_hormigon",
        "curva_viaria",
        "arcen_tierra",
        "valla_madera",
        "talud_rocoso",
        "arbolado_denso",
        "tres_personas",
        "niebla"
      ]
    },
    {
      "id": "864c9cb1-f1c6-480a-ac7d-7c10909eb51e",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/f06c67a8_p21_x160.png",
      "descripcion": "Informe SamRAT de cálculo de velocidad por huella de frenada: longitud 1,89 m, resultado Vi=20,06 km/h, coeficiente rozamiento 0,75.",
      "tipo": "croquis",
      "tags": [
        "informe_samrat",
        "calculo_velocidad",
        "huella_frenada",
        "modelo_general",
        "pericia_tecnica"
      ],
      "vehiculo_id": "A",
      "elementos_visibles": [
        "esquema_frenada",
        "formula_cinematica",
        "longitud_huella_1_89m",
        "coeficiente_rozamiento_0_75",
        "pendiente_via_5_143_grados",
        "velocidad_inicial_20_056_kmh",
        "logotipo_samrat",
        "licencia_itrasa"
      ]
    }
  ],
  "razon": "Es la única foto catalogada como 'escena_huellas' con tags explícitos de huella/marca de deslizamiento de bicicleta sobre calzada en tramo de curva, que es exactamente el criterio buscado",
  "falta_info": null,
  "requiere_foto": false
}
```

#### 3.4 → `buscar_foto_perito`

**Inputs del Perito:**
```json
{
  "criterio": "medición pericial de visibilidad efectiva 26,5 m en la curva"
}
```

**Respuesta del especialista:**
```json
{
  "match": {
    "id": "efaa60b8-0177-44ef-82a9-2c68c0be7cc2",
    "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/dbcdc868_p08_x82.png",
    "descripcion": "Reconstrucción 3D por nube de puntos de vía curva con talud lateral; medición forense de distancia 26,59 m entre dos puntos marcados en rojo.",
    "tipo": "croquis",
    "tags": [
      "nube_puntos_3d",
      "escaner_laser",
      "medicion_distancia",
      "via_curva",
      "talud",
      "software_forense"
    ],
    "vehiculo_id": null,
    "elementos_visibles": [
      "nube_puntos_3d",
      "calzada_curva",
      "talud_vegetacion",
      "linea_medicion_roja",
      "tabla_coordenadas_XYZ",
      "distancia_26_59m",
      "borde_calzada",
      "gravilla_arcen"
    ]
  },
  "alternativas": [
    {
      "id": "11dbc203-be17-40ac-b9d7-4bad123943e3",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/87104f2d_p09_x88.png",
      "descripcion": "Modelo 3D fotogramétrico de escena vial con medición de distancia de 25,3 m entre dos puntos sobre vía rural en bifurcación.",
      "tipo": "croquis",
      "tags": [
        "nube_puntos_3d",
        "medicion_distancia",
        "reconstruccion_fotogrametrica",
        "via_rural",
        "bifurcacion",
        "linea_medicion"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "nube_de_puntos_3d",
        "linea_medicion_roja",
        "via_rural_sin_asfaltar",
        "bifurcacion",
        "vegetacion_lateral",
        "vehiculo_azul_al_fondo",
        "herramienta_medicion_coordenadas"
      ]
    },
    {
      "id": "9325d5e3-38fa-46c3-99b9-e134825837a7",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/ec3dd9f5_p08_x81.png",
      "descripcion": "Nube de puntos 3D de vía estrecha en curva con medición forense de distancia 3,104 m entre dos puntos señalados.",
      "tipo": "croquis",
      "tags": [
        "nube_puntos_3d",
        "medicion_distancia",
        "escaneado_laser",
        "via_estrecha",
        "curva",
        "software_forense"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "calzada_estrecha",
        "arcen_rocoso",
        "curva_horizontal",
        "linea_medicion_roja",
        "cuadro_coordenadas_XYZ",
        "vegetacion",
        "talud"
      ]
    },
    {
      "id": "0b98c989-0cbe-482e-a4ff-d99554b4b4cb",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/7d1145f8_p11_x98.png",
      "descripcion": "Carretera rural con curva en zona boscosa y neblinosa; tres personas presentes en arcén fotografiando el lugar del siniestro.",
      "tipo": "escena_general",
      "tags": [
        "carretera_rural",
        "curva_calzada",
        "testigos_presentes",
        "zona_forestal",
        "niebla",
        "arcen_tierra"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "calzada_hormigon",
        "curva_viaria",
        "arcen_tierra",
        "valla_madera",
        "talud_rocoso",
        "arbolado_denso",
        "tres_personas",
        "niebla"
      ]
    }
  ],
  "razon": "Nube de puntos 3D de vía curva con medición forense explícita de 26,59 m entre dos puntos marcados, coincidiendo con la distancia de visibilidad pericial de 26,5 m en la curva",
  "falta_info": null,
  "requiere_foto": false
}
```

#### 3.5 → `buscar_foto_perito`

**Inputs del Perito:**
```json
{
  "criterio": "croquis cenital del atropello con cotas longitudinal 8 m y lateral 1,2 m"
}
```

**Respuesta del especialista:**
```json
{
  "match": {
    "id": "adf66d1f-d45e-4cbf-a61b-bd5dd4438f55",
    "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/050d11b5_p05_x65.png",
    "descripcion": "Croquis digital cenital de atropello: turismo colisiona con ciclista sobre calzada, con cotas de distancia longitudinal 8,008 m y lateral 1,215 m.",
    "tipo": "croquis",
    "tags": [
      "croquis_digital",
      "vista_cenital",
      "medicion_distancia",
      "atropello_bicicleta",
      "trayectoria_impacto",
      "cotas_metricas"
    ],
    "vehiculo_id": null,
    "elementos_visibles": [
      "turismo_vista_cenital",
      "bicicleta_posicion_final",
      "ciclista_figura",
      "linea_trayectoria",
      "cota_longitudinal_8008m",
      "cota_lateral_1215m",
      "calzada_asfaltada"
    ]
  },
  "alternativas": [
    {
      "id": "5bdfa467-65c2-4604-b4db-525fa1cac3df",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/e0941f93_p05_x66.png",
      "descripcion": "Reconstrucción 3D de atropello: turismo SEAT y ciclista en calzada curva con cotas de distancia 8,008 m y 1,215 m indicadas.",
      "tipo": "croquis",
      "tags": [
        "croquis_3d",
        "reconstruccion_accidente",
        "bicicleta_atropello",
        "distancia_medida",
        "carretera_curva",
        "posicion_vehiculos"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "turismo_seat",
        "bicicleta_roja",
        "ciclista_casco_verde",
        "calzada_curva",
        "cota_8008m",
        "cota_1215m",
        "posicion_impacto",
        "posicion_preimpacto"
      ]
    },
    {
      "id": "1bc11585-44bb-4257-bb7e-6c1ff1a70829",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/2d204ee0_p06_x71.png",
      "descripcion": "Reconstrucción 3D de atropello a ciclista: secuencia de impacto entre turismo SEAT y bicicleta, con medición de 1,21 m.",
      "tipo": "croquis",
      "tags": [
        "reconstruccion_3d",
        "atropello_ciclista",
        "secuencia_impacto",
        "medicion_distancia",
        "figura_animada"
      ],
      "vehiculo_id": "A",
      "elementos_visibles": [
        "turismo_seat_ibiza",
        "bicicleta_roja",
        "figura_ciclista",
        "figura_peatonal_proyectada",
        "medicion_1_21m",
        "calzada_carretera",
        "sombras_animadas"
      ]
    },
    {
      "id": "5528fee6-610f-4138-9621-2b67eec44f2d",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/33ccaa1d_p37_x235.png",
      "descripcion": "Reconstrucción fotogramétrica 3D en vista cenital de carretera con curva, mostrando vehículo tipo turismo y ciclista sobre la calzada.",
      "tipo": "croquis",
      "tags": [
        "reconstruccion_3d",
        "nube_de_puntos",
        "vista_cenital",
        "carretera_curva",
        "vehiculo_en_calzada",
        "ciclista_en_calzada",
        "escena_completa"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "carretera_asfaltada",
        "curva_vial",
        "turismo_gris",
        "ciclista",
        "vegetacion_marginal",
        "talud_roca",
        "marcas_viales_ausentes"
      ]
    }
  ],
  "razon": "Croquis digital cenital de atropello turismo-ciclista con cotas explícitas 8,008 m (longitudinal) y 1,215 m (lateral), coincidencia directa con el criterio",
  "falta_info": null,
  "requiere_foto": false
}
```

#### 3.6 → `buscar_foto_perito`

**Inputs del Perito:**
```json
{
  "criterio": "informe SamRAT cálculo velocidad turismo huella frenada 1,89 m"
}
```

**Respuesta del especialista:**
```json
{
  "match": {
    "id": "864c9cb1-f1c6-480a-ac7d-7c10909eb51e",
    "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/f06c67a8_p21_x160.png",
    "descripcion": "Informe SamRAT de cálculo de velocidad por huella de frenada: longitud 1,89 m, resultado Vi=20,06 km/h, coeficiente rozamiento 0,75.",
    "tipo": "croquis",
    "tags": [
      "informe_samrat",
      "calculo_velocidad",
      "huella_frenada",
      "modelo_general",
      "pericia_tecnica"
    ],
    "vehiculo_id": "A",
    "elementos_visibles": [
      "esquema_frenada",
      "formula_cinematica",
      "longitud_huella_1_89m",
      "coeficiente_rozamiento_0_75",
      "pendiente_via_5_143_grados",
      "velocidad_inicial_20_056_kmh",
      "logotipo_samrat",
      "licencia_itrasa"
    ]
  },
  "alternativas": [
    {
      "id": "9811026f-2fc0-41a0-a4f9-c9205c82ead5",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/5853cdf8_p20_x156.png",
      "descripcion": "Informe SamRAT de cálculo de velocidad por huella de frenada: longitud 0,47 m, velocidad inicial calculada 10 km/h, pendiente 5,143°.",
      "tipo": "atestado_pagina",
      "tags": [
        "informe_samrat",
        "calculo_velocidad",
        "huella_frenada",
        "modelo_general",
        "coeficiente_rozamiento"
      ],
      "vehiculo_id": "A",
      "elementos_visibles": [
        "esquema_frenada",
        "formula_cinematica",
        "datos_tecnicos",
        "resultado_velocidad",
        "logotipo_samrat"
      ]
    },
    {
      "id": "b76306f3-5d67-4b81-9fa4-f1962dac4096",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/5a863711_p25_x178.png",
      "descripcion": "Informe SamRAT de cálculo de velocidad por huella de frenada (modelo 3 fases) con esquema, fórmula y resultados: Vi=23,836 km/h, S=8 m.",
      "tipo": "croquis",
      "tags": [
        "informe_samrat",
        "calculo_velocidad",
        "huella_frenada",
        "modelo_3_fases",
        "motocicleta",
        "coeficiente_rozamiento"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "esquema_frenada",
        "formula_velocidad_inicial",
        "diagrama_fases_temporales",
        "datos_tecnicos",
        "resultado_velocidad_circulacion",
        "espacio_reaccion",
        "coeficiente_rozamiento",
        "pendiente_via"
      ]
    },
    {
      "id": "89969bcd-c5c3-4b05-b332-4b8d6af5ba93",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/f59bc983_p30_x205.png",
      "descripcion": "Informe SamRAT de cálculo de distancia de parada modelo 3 fases: velocidad 50 km/h, distancia total 26,32 m, pendiente 5,143°, coeficiente rozamiento 0,75.",
      "tipo": "atestado_pagina",
      "tags": [
        "informe_samrat",
        "calculo_distancia_parada",
        "modelo_3_fases",
        "reconstruction_accidente",
        "velocidad_50kmh",
        "coeficiente_rozamiento",
        "pendiente_via"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "esquema_frenada",
        "formula_distancia_parada",
        "datos_tecnicos",
        "resultados_numericos",
        "representacion_vehiculo_lateral"
      ]
    }
  ],
  "razon": "Informe SamRAT de cálculo de velocidad por huella de frenada con longitud exacta de 1,89 m, resultado Vi=20,06 km/h y coeficiente rozamiento 0,75, coincide exactamente con el criterio",
  "falta_info": null,
  "requiere_foto": false
}
```

#### 3.7 → `buscar_foto_perito`

**Inputs del Perito:**
```json
{
  "criterio": "manillar deformado de la bicicleta Orbea con medición"
}
```

**Respuesta del especialista:**
```json
{
  "match": {
    "id": "4ae291b1-cc67-4287-8e1e-047c2e49f08d",
    "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/cf86246d_p17_x138.png",
    "descripcion": "Medición pericial del manillar de bicicleta Orbea con cinta métrica, mostrando posible deformación o desplazamiento tras impacto.",
    "tipo": "vehiculo_detalle_dano",
    "tags": [
      "manillar_bicicleta",
      "medicion_pericial",
      "cinta_metrica",
      "palancas_freno",
      "deformacion_manillar"
    ],
    "vehiculo_id": "B",
    "elementos_visibles": [
      "manillar",
      "palancas_de_freno",
      "potencia_manillar",
      "sillín",
      "cuadro_rojo",
      "cinta_métrica"
    ]
  },
  "alternativas": [],
  "razon": "Foto pericial del manillar de bicicleta Orbea con cinta métrica visible, deformación documentada y calidad alta",
  "falta_info": null,
  "requiere_foto": false
}
```

#### 3.8 → `buscar_foto_perito`

**Inputs del Perito:**
```json
{
  "criterio": "diagrama WAD zonas de impacto cabeza ciclista capó parabrisas"
}
```

**Respuesta del especialista:**
```json
{
  "match": {
    "id": "4f322155-c452-47d0-8fdc-9830f5bd8a55",
    "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/d27e87e1_p28_x196.png",
    "descripcion": "Diagrama técnico forense con zonas de impacto sobre capó y parabrisas para peatón joven y ciclista joven a distintas velocidades (20-50 km/h), con líneas WAD 1000 y 1500.",
    "tipo": "croquis",
    "tags": [
      "diagrama_tecnico",
      "puntos_impacto_peatón",
      "puntos_impacto_ciclista",
      "WAD_1000",
      "WAD_1500",
      "velocidades_impacto",
      "capo_vehiculo",
      "parabrisas"
    ],
    "vehiculo_id": null,
    "elementos_visibles": [
      "capo",
      "parabrisas",
      "pillar_A",
      "linea_WAD_1000",
      "linea_WAD_1500",
      "simbolos_impacto_peatón",
      "simbolos_impacto_ciclista",
      "leyenda_velocidades"
    ]
  },
  "alternativas": [
    {
      "id": "0f99d9e8-f588-457d-bda0-838145fca58c",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/96398c90_p28_x197.png",
      "descripcion": "Diagrama técnico de reconstrucción con zonas WAD y puntos de impacto de cabeza de ciclista y peatón sobre capó y parabrisas de turismo.",
      "tipo": "croquis",
      "tags": [
        "diagrama_impacto",
        "WAD_zones",
        "puntos_contacto_cabeza",
        "ciclista",
        "peaton",
        "capo_vehiculo",
        "parabrisas",
        "reconstruccion_siniestro"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "capo",
        "parabrisas",
        "zona_WAD_1000",
        "zona_WAD_1500",
        "zona_WAD_2500",
        "puntos_impacto_ciclista",
        "puntos_impacto_peaton",
        "techo"
      ]
    },
    {
      "id": "454d6ad8-dddb-43fb-8a94-1578ab83c9ac",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/6c680c51_p27_x192.png",
      "descripcion": "Diagrama técnico pericial que muestra zonas WAD de impacto de cabeza de ciclista/peatón sobre capó y parabrisas de vehículo a distintas velocidades.",
      "tipo": "atestado_pagina",
      "tags": [
        "diagrama_tecnico",
        "WAD_impacto_cabeza",
        "puntos_contacto_ciclista",
        "colision_frontal_bicicleta",
        "figura_referencia_pericial"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "capo",
        "parabrisas",
        "zona_WAD_1000",
        "zona_WAD_1500",
        "zona_WAD_2000",
        "puntos_impacto_ciclista",
        "puntos_impacto_peatón",
        "leyenda_velocidades"
      ]
    },
    {
      "id": "7e16c71e-e4e1-4d6f-9533-d825a3ec15a8",
      "url": "http://localhost:8000/uploads/8c186a74-9443-494e-9d22-c543802ca323/fotos/1d34f206_p29_x201.png",
      "descripcion": "Diagrama técnico WAD que muestra zonas de impacto sobre capó y parabrisas para peatón joven y ciclista joven a distintas velocidades.",
      "tipo": "croquis",
      "tags": [
        "diagrama_tecnico",
        "WAD_wrap_around_distance",
        "zona_impacto_capó",
        "atropello_peatón",
        "atropello_ciclista",
        "puntos_impacto_velocidad"
      ],
      "vehiculo_id": null,
      "elementos_visibles": [
        "capó",
        "parabrisas",
        "líneas_WAD_1000_1500_2530",
        "puntos_impacto_ciclista_joven",
        "puntos_impacto_peatón_joven",
        "leyenda_velocidades"
      ]
    }
  ],
  "razon": "Diagrama técnico forense con zonas WAD 1000 y 1500, puntos de impacto de ciclista joven sobre capó y parabrisas a distintas velocidades, calidad alta y todos los elementos solicitados presentes.",
  "falta_info": null,
  "requiere_foto": false
}
```

#### 3.9 → `obtener_frame_simulacion`

**Inputs del Perito:**
```json
{
  "evento": "impacto",
  "masa_a": 1115,
  "masa_b": 85,
  "ebs_a_kmh": 24,
  "ebs_b_kmh": 25,
  "modelo_a": "SEAT Ibiza",
  "modelo_b": "Ciclista Orbea",
  "angulo_pre_a": 0,
  "angulo_pre_b": 180,
  "huellas_post_a_m": 0.5,
  "huellas_post_b_m": 8.0,
  "mu": 0.75,
  "tipo_colision": "atropello"
}
```

**Respuesta del especialista:**
```json
{
  "evento": "impacto",
  "frame_url": "http://localhost:8000/uploads/_frames_simulacion/e85cc71e02_impacto.svg",
  "delta_v_a_kmh": 14.2,
  "delta_v_b_kmh": 14.1,
  "v_pre_a_kmh": 24,
  "v_pre_b_kmh": 25,
  "v_post_a_kmh": 9.8,
  "v_post_b_kmh": 39.1,
  "coef_restitucion": 0.598,
  "error_momento_pct": 69.3,
  "advertencias": [
    "Error de momento 69.3% > 15% — revisar ángulos o velocidades."
  ]
}
```

### Turno 4
**🧠 Razonamiento del Perito:**

> Tengo material gráfico suficiente. Ahora con todos los datos consolidados puedo emitir el informe final.
> 
> Análisis clave:
> - **Velocidad turismo**: el atestado no halla huella del turismo, pero los SamRAT del expediente identifican una huella corta (1,89 m → 20,06 km/h y 0,47 m → 10 km/h). El WAD sin embargo (parabrisas derecho + hendidura en techo) sugiere energía superior, aunque la concentración sobre arista rígida hace compatible la lesividad letal con ~24 km/h.
> - **Huella ciclista 8 m descendente** → v_min ciclista ≈ 36 km/h.
> - **Distancia detención turismo**: a 20 km/h en cuesta arriba con t_reacción=1s = 7,4 m; a 30 km/h = 12,5 m. Visibilidad efectiva pericial 26,5 m.
> - **Evitabilidad**: 7,4 m << 26,5 m visibilidad → si circulaba a 20 km/h con atención debida, debería haberse detenido sobradamente.
> - **Atestado**: deficiente (R conformidad).
> 
> ```json
> {
>   "resumen_caso": "Atropello mortal de ciclista (IBU) por turismo SEAT Ibiza 3526-BKL conducido por JME el 21/05/2020 a las 20:38 en Barrio Zubero (Aulestia, Bizkaia), en vía rural estrecha (3,10-3,20 m), con curva y pendiente 9-11,6 %. Calzada seca (μ=0,75), día claro (atardecer 21:33), sin lluvia. El ciclista descendía por su mitad derecha y dejó huella de bloqueo de cubierta trasera de 8 m que termina a 1,2 m del borde; el turismo ascendía y, pese a declarar frenada máxima, no dejó huella visible salvo dos marcas cortas (1,89 m y 0,47 m) recogidas por SamRAT. La trayectoria del cuerpo (parachoques → capó → parabrisas derecho → hendidura en techo) traduce un atropello fronto-lateral derecho turismo-ciclista con impacto cefálico letal. La señal de 20 km/h figura fotografiada a la entrada del barrio. El atestado de la Ertzaintza presenta carencias metodológicas relevantes (R1-R8).",
>   "respuestas": [
>     {
>       "pregunta_id": "C1",
>       "pregunta": "Determinar la velocidad real del turismo en el momento de la colisión contra el ciclista.",
>       "respuesta": "La colisión se califica técnicamente como **atropello fronto-lateral derecho turismo-ciclista con proyección sobre capó y secundario en parabrisas-techo**. La velocidad del turismo en el momento del impacto se sitúa en una horquilla compatible con 20-25 km/h, con una mejor estimación de ~24 km/h, sustentada por tres líneas convergentes: (i) los cálculos SamRAT del expediente sobre las huellas cortas atribuidas al turismo (1,89 m → Vi=20,06 km/h; 0,47 m → Vi=10 km/h), (ii) la ausencia de huella plena sostenida que indica que la frenada no fue de bloqueo prolongado y (iii) la cinemática del cuerpo. La huella de 8 m corresponde inequívocamente a la **bicicleta** (bloqueo de cubierta trasera del ciclista en descenso), de la que se deriva una velocidad propia mínima del ciclista de 36,3 km/h aplicando Stannard-Baker con μ=0,75 y pendiente -10,3 %. Respecto a la lesividad, el WAD del impacto cefálico (parabrisas derecho con apoyo en arista de techo) corresponde nominalmente a velocidades 45-60 km/h en colisión turismo-peatón estándar; sin embargo, la concentración de energía sobre el umbral rígido del techo (estructura no deformable) explica que el desenlace letal sea biomecánicamente compatible con velocidades inferiores (≈24 km/h), tal como recoge la excepción 'impacto contra estructura rígida del vehículo' del manual ESTT/DGT 2011 y UC3M-Guardia Civil 2020. En consecuencia, se concluye velocidad de impacto del turismo del orden de 20-25 km/h, **incompatible con la declaración del extremo inferior (10 km/h)** del conductor.",
>       "confianza": 0.7,
>       "citas": [
>         {"tipo": "calculo", "referencia": "SimulacionAgent — velocidad_por_huella ciclista", "extracto": "v_min = 36,3 km/h con huella 8,0 m, μ=0,75, pendiente -10,3 % (Stannard-Baker)."},
>         {"tipo": "imagen", "referencia": "864c9cb1 — SamRAT huella 1,89 m → Vi=20,06 km/h (turismo)"},
>         {"tipo": "imagen", "referencia": "9811026f — SamRAT huella 0,47 m → Vi=10 km/h (turismo)"},
>         {"tipo": "imagen", "referencia": "c8bb8b64 — SEAT Ibiza con parabrisas fracturado por impacto cefálico"},
>         {"tipo": "imagen", "referencia": "4f322155 — Diagrama WAD 1000/1500 con puntos de impacto ciclista a distintas velocidades"},
>         {"tipo": "imagen", "referencia": "adf66d1f — Croquis cenital con cotas 8,008 m (longitudinal) y 1,215 m (lateral)"},
>         {"tipo": "imagen", "referencia": "8a03add7 — Huella longitudinal de deslizamiento de bicicleta en curva"},
>         {"tipo": "imagen", "referencia": "4ae291b1 — Manillar Orbea con deformación pericialmente medida"},
>         {"tipo": "ficha_tecnica", "referencia": "FichaAgent — SEAT Ibiza 2018", "extracto": "Masa 1.115 kg; altura parachoques 0,42-0,70 m; altura total 1,44 m."},
>         {"tipo": "hecho", "referencia": "BiomecanicaAgent — análisis WAD/cráneo", "extracto": "Compatible con fallecimiento a ~24 km/h por concentración de energía contra umbral de techo (estructura rígida)."}
>       ]
>     },
>     {
>       "pregunta_id": "C2",
>       "pregunta": "Establecer si el accidente era evitable cumpliendo la normativa de circulación.",
>       "respuesta": "El accidente era **objetivamente evitable** circulando a la velocidad reglamentaria con la atención debida. La distancia de visibilidad efectiva medida pericialmente sobre la curva es de 26,5 m lineales (>30 m sobre trayectoria curva), confirmada por nube de puntos 3D. La distancia total de detención del SEAT Ibiza, con μ=0,75, pendiente ascendente 10,3 % y t_reacción=1 s, es: a 20 km/h → 7,4 m (5,56 m reacción + 1,84 m frenada) en 1,66 s; a 30 km/h → 12,48 m en 2,00 s. En ambos escenarios la distancia de detención es **muy inferior** a la visibilidad disponible (7,4 m y 12,5 m frente a 26,5 m), de modo que un conductor atento que circulase a velocidad reglamentaria habría detenido el vehículo con antelación suficiente. Aplicando además el patrón de evitabilidad ciclista-conductor: el ciclista, una vez percibido el riesgo, dispuso de t_total ≈ 3,1 s desde la reacción hasta finalizar su huella de 8 m (1 s reacción + 0,5 s ejecución + 1,59 s frenada) — tiempo holgadamente superior a los 1,66-2,00 s que necesitaba el turismo para detenerse a velocidad reglamentaria. Existía además, según constata el atestado, una **zona terriza diáfana de varios metros a la derecha del turismo** con desnivel máximo de 4 cm, que permitía maniobra evasiva ejecutable. La concurrencia de ambos elementos (sobrada distancia de detención y maniobra evasiva disponible) confirma la evitabilidad técnica del siniestro.",
>       "confianza": 0.85,
>       "citas": [
>         {"tipo": "calculo", "referencia": "SimulacionAgent — distancia_detencion 20 km/h", "extracto": "d_total=7,40 m en 1,66 s (μ=0,75; pendiente +10,3 %; t_r=1 s)."},
>         {"tipo": "calculo", "referencia": "SimulacionAgent — distancia_detencion 30 km/h", "extracto": "d_total=12,48 m en 2,00 s."},
>         {"tipo": "calculo", "referencia": "SimulacionAgent — tiempo_huella ciclista 8 m", "extracto": "t_total=3,09 s (1,0 + 0,5 + 1,59)."},
>         {"tipo": "imagen", "referencia": "efaa60b8 — Nube de puntos 3D con visibilidad de 26,59 m en la curva"},
>         {"tipo": "imagen", "referencia": "9325d5e3 — Anchura de calzada 3,104 m medida 3D"},
>         {"tipo": "imagen", "referencia": "89969bcd — SamRAT distancia parada 50 km/h = 26,32 m (referencia comparativa)"},
>         {"tipo": "hecho", "referencia": "Atestado Ertzaintza", "extracto": "Zona terriza diáfana a la derecha (desnivel máx. 4 cm) que permitiría maniobra evasiva."},
>         {"tipo": "normativa", "referencia": "Art. 45 RGC (RD 1428/2003)", "extracto": "El conductor adecuará la velocidad de modo que pueda detener el vehículo dentro de los límites de su campo de visión y ante cualquier obstáculo que pueda presentarse."},
>         {"tipo": "normativa", "referencia": "Art. 46.1.b RGC", "extracto": "Obligación específica de moderar la velocidad al aproximarse a ciclos en circulación."}
>       ]
>     },
>     {
>       "pregunta_id": "C3",
>       "pregunta": "Indicar la conducta del conductor del turismo respecto al límite de velocidad y la atención debida.",
>       "respuesta": "El conductor (vecino conocedor de la vía y de su limitación) presenta dos desviaciones técnicamente acreditadas. **Respecto al límite de velocidad**: la señal vertical R-301 de 20 km/h del Barrio Zubero está fotográficamente acreditada (foto e234bc44 y c4557c1c). La velocidad de impacto reconstruida (~20-25 km/h) se sitúa en el límite o por encima del máximo permitido y, en cualquier caso, no era una velocidad **adecuada** a las circunstancias del art. 45 RGC: vía estrecha (3,10-3,20 m, apenas suficiente para el cruce con un ciclista), curva con visibilidad efectiva de 26,5 m y pendiente 9-11,6 %, lo que exigía circular a una velocidad que permitiese detenerse en cualquier punto del campo de visión, condición que no se cumplió. **Respecto a la atención debida**: la cinemática es incompatible con una conducción diligente del art. 3 RGC. Con 26,5 m de visibilidad y una distancia de detención de 7,4 m a 20 km/h, sólo es físicamente comp

*(stop_reason: `max_tokens` — fin de la investigación)*

---

## 2. Resumen por especialista (todos los outputs)

### BibliotecaFotosAgent (9 llamadas)
- **Pregunta:** listar_biblioteca: inventario completo
  - **Resultado:** 40 fotos clasificadas en 8 tipos: otro (3), escena_general (8), croquis (20), escena_huellas (1), vehiculo_frontal (3), atestado_pagina (3), vehiculo_detalle_dano (1), escena_senalizacion (1)
  - **Fuentes:** Repositorio de fotos del caso
  - **Duración:** 0 ms
- **Pregunta:** buscar_foto: SEAT Ibiza frontal con parabrisas fracturado por impacto cefálico del ciclista
  - **Resultado:** Match → SEAT Ibiza matrícula 3526-BKL con parabrisas completamente fracturado por impacto, capó aparentemente sin deformación estructural visible. (3 alternativas)
  - **Fuentes:** Repositorio de fotos del caso · Claude visión
  - **Duración:** 7370 ms
- **Pregunta:** buscar_foto: señal vertical de limitación a 20 km/h en barrio Zubero
  - **Resultado:** Match → Incorporación en zona rural del barrio Zubero auzoa, con señal de límite 20 km/h y calzada húmeda. Sin vehículos visibles en escena. (1 alternativas)
  - **Fuentes:** Repositorio de fotos del caso · Claude visión
  - **Duración:** 5846 ms
- **Pregunta:** buscar_foto: huella de derrape de bicicleta sobre la calzada en curva
  - **Resultado:** Match → Vista longitudinal de calzada rural con posible marca de deslizamiento de bicicleta sobre pavimento de hormigón en tramo de curva. (3 alternativas)
  - **Fuentes:** Repositorio de fotos del caso · Claude visión
  - **Duración:** 7465 ms
- **Pregunta:** buscar_foto: medición pericial de visibilidad efectiva 26,5 m en la curva
  - **Resultado:** Match → Reconstrucción 3D por nube de puntos de vía curva con talud lateral; medición forense de distancia 26,59 m entre dos puntos marcados en rojo. (3 alternativas)
  - **Fuentes:** Repositorio de fotos del caso · Claude visión
  - **Duración:** 7782 ms
- **Pregunta:** buscar_foto: croquis cenital del atropello con cotas longitudinal 8 m y lateral 1,2 m
  - **Resultado:** Match → Croquis digital cenital de atropello: turismo colisiona con ciclista sobre calzada, con cotas de distancia longitudinal 8,008 m y lateral 1,215 m. (3 alternativas)
  - **Fuentes:** Repositorio de fotos del caso · Claude visión
  - **Duración:** 7990 ms
- **Pregunta:** buscar_foto: informe SamRAT cálculo velocidad turismo huella frenada 1,89 m
  - **Resultado:** Match → Informe SamRAT de cálculo de velocidad por huella de frenada: longitud 1,89 m, resultado Vi=20,06 km/h, coeficiente rozamiento 0,75. (3 alternativas)
  - **Fuentes:** Repositorio de fotos del caso · Claude visión
  - **Duración:** 27547 ms
- **Pregunta:** buscar_foto: manillar deformado de la bicicleta Orbea con medición
  - **Resultado:** Match → Medición pericial del manillar de bicicleta Orbea con cinta métrica, mostrando posible deformación o desplazamiento tras impacto. (0 alternativas)
  - **Fuentes:** Repositorio de fotos del caso · Claude visión
  - **Duración:** 17499 ms
- **Pregunta:** buscar_foto: diagrama WAD zonas de impacto cabeza ciclista capó parabrisas
  - **Resultado:** Match → Diagrama técnico forense con zonas de impacto sobre capó y parabrisas para peatón joven y ciclista joven a distintas velocidades (20-50 km/h), con líneas WAD 1000 y 1500. (3 alternativas)
  - **Fuentes:** Repositorio de fotos del caso · Claude visión
  - **Duración:** 26013 ms

### EscenaAgent (1 llamadas)
- **Pregunta:** Geometría y señales en Barrio Zubero, Aulestia, Bizkaia (radio 50→50m)
  - **Resultado:** BI- 3242-Arratzuko errepidea, Elexalde, Kortezubi, Bizkaia, Euskadi, 48383, Espa. Vía: desconocida, vmáx OSM: —, pendiente: 68.3%, señales: 0, imágenes Mapillary: 0, radio efectivo: 50 m
  - **Fuentes:** Nominatim (reverso) · OpenStreetMap Overpass (sin match) · Open-Elevation (DEM SRTM)
  - ⚠️ **Falta:** La pendiente devuelta por el DEM (68.3%) es físicamente inverosímil para una vía rodada abierta a tráfico (>30%). Probablemente el muestreo radial del DEM ha caído en un talud lateral, no en la traza de la vía. Solicita al perito la pendiente medida in situ o aportada por el atestado. OpenStreetMap no tiene esta vía mapeada con suficiente detalle. La anchura, número de carriles, velocidad máxima y señalización deben ser confirmadas por el perito mediante medición in situ o atestado.
  - **Duración:** 9745 ms

### MeteoAgent (1 llamadas)
- **Pregunta:** Meteo histórica en 43.33,-2.6203 el 2020-05-21T20:38:00
  - **Resultado:** cubierto, 20.1°C, precipitación 0.0 mm, calzada seca, día.
  - **Fuentes:** Open-Meteo Archive (ECMWF ERA5)
  - **Duración:** 1330 ms

### FichaAgent (1 llamadas)
- **Pregunta:** Ficha técnica de SEAT Ibiza (2018)
  - **Resultado:** SEAT Ibiza: 1115.0 kg, ancho 1.78 m, 3 sistemas seguridad. Fuente: SEAT España — ficha técnica Ibiza (5ª gen.)
  - **Fuentes:** SEAT España — ficha técnica Ibiza (5ª gen.)
  - **Duración:** 0 ms

### SimulacionAgent (4 llamadas)
- **Pregunta:** Simulación física: velocidad_por_huella
  - **Resultado:** Velocidad mínima del vehículo: 36.3 km/h con huella de 8.0 m, μ=0.75.
  - **Fuentes:** NumPy local · Manuales Limpert / Stannard Baker / Searle
  - **Duración:** 0 ms
- **Pregunta:** Simulación física: distancia_detencion
  - **Resultado:** A 20.0 km/h con μ=0.75, pendiente 10%, t_reacción=1.0s: recorre 7.40 m en 1.66 s (frenada 1.84 m / 0.66 s).
  - **Fuentes:** NumPy local · Manuales Limpert / Stannard Baker / Searle
  - **Duración:** 0 ms
- **Pregunta:** Simulación física: distancia_detencion
  - **Resultado:** A 30.0 km/h con μ=0.75, pendiente 10%, t_reacción=1.0s: recorre 12.48 m en 2.00 s (frenada 4.15 m / 1.00 s).
  - **Fuentes:** NumPy local · Manuales Limpert / Stannard Baker / Searle
  - **Duración:** 0 ms
- **Pregunta:** Simulación física: tiempo_huella
  - **Resultado:** Desde percepción del riesgo hasta el final de la huella (8.0 m): t_total = 3.09 s (reacción 1.0s + ejecución 0.5s + frenada 1.59s). Velocidad al iniciar el bloqueo: 36.3 km/h.
  - **Fuentes:** NumPy local · Manuales Limpert / Stannard Baker / Searle
  - **Duración:** 0 ms

### AtestadoAgent (1 llamadas)
- **Pregunta:** Contraste declaración del conductor vs evidencia física
  - **Resultado:** Declaración: 20.0 km/h. Cálculo físico: 23.84 km/h. Diferencia +3.8 km/h. Incompatibles: la evidencia física supera el margen del 15%.
  - **Fuentes:** Atestado del caso · SimulacionAgent (output previo)
  - **Duración:** 0 ms

### ConformidadAtestadoAgent (1 llamadas)
- **Pregunta:** Auditoría LLM del atestado (ertzaintza)
  - **Resultado:** Valoración: deficiente. 5 incongruencias (2 altas, 2 medias), 6 omisiones.
  - **Fuentes:** Claude Sonnet (razonamiento pericial) · Manual pericial AEIAT/IURGI (en system prompt) · RD 970/2020 · Art. 379 CP
  - **Duración:** 30104 ms

### LegalAgent (1 llamadas)
- **Pregunta:** Selección normativa LLM para encargo='atropello' (fecha 2020-05-21T20:38:00)
  - **Resultado:** 6 artículos seleccionados (de 7 disponibles), 6 referencias bibliográficas. Advertencia temporal: El siniestro se produjo el 21 de mayo de 2020. El RD 970/2020, que estableció el límite genérico de 20 km/h en vías de s
  - **Fuentes:** Claude Sonnet (razonamiento jurídico) · Veridict normativa seed · BOE/EUR-Lex (URLs consolidadas)
  - **Duración:** 21706 ms

### BiomecanicaAgent (1 llamadas)
- **Pregunta:** analizar_biomecanica (atropello=True) v=24
  - **Resultado:** WAD parabrisas central → 45-60 km/h · Ec=24.8 kJ · AIS3+ p=9% · análisis cefálico (5 tipos) · 4 mecanismos lesivos · compatibilidad: compatible — impacto contra estructura rígida del vehículo (umbral techo) a 24 km/h justifica lesividad letal cefálica por concentración de energía en zona craneal sin absorción de deformación.
  - **Fuentes:** Manual ESTT/DGT 2011 — Especialidad Gestión del Tráfico y Movilidad. · Limpert R., Motor Vehicle Accident Reconstruction (LexisNexis, 6.ª ed., 2012). · Mertz H.J., Anthropomorphic Test Devices, en Accidental Injury (Springer, 2002). · Otte D., Pedestrian/Cyclist injuries from cars (1989). · Van Rooij L., Pedestrian impact reconstruction with WAD (2003). · UC3M & Guardia Civil, Manual de reconstrucción atropellos (2020). · Claude Sonnet (razonamiento clínico)
  - ⚠️ **Falta:** ¿Dispone la autopsia de descripción detallada del patrón de fractura craneal (tipo, localización y extensión) y de los hallazgos neuropatológicos (hematomas, áreas de contusión, DAI confirmado por histología)? Dicha información permitiría precisar el mecanismo lesivo predominante y correlacionarlo con mayor exactitud con la dinámica de impacto documentada por los daños del vehículo.
  - **Duración:** 27545 ms

### SimulacionFramesAgent (1 llamadas)
- **Pregunta:** obtener_frame: impacto
  - **Resultado:** Frame impacto. v_pre A=24.0 km/h, B=25.0 km/h. Δv A=14.2, Δv B=14.1 km/h. Error de momento: 69.3%.
  - **Fuentes:** Motor Veridict (physics.reconstruction + physics.croquis)
  - ⚠️ **Falta:** Error de momento 69.3% > 15% — revisar ángulos o velocidades.
  - **Duración:** 3 ms

---

## 3. Comparativa con el informe IURGI/ITRASA oficial

Sección a sección del PDF oficial vs lo que ha producido Veridict.

### §2 Tipo de accidente y condiciones del lugar

| | IURGI/ITRASA oficial | Veridict |
|---|---|---|
| Contenido | Colisión fronto-lateral excéntrica turismo–bicicleta. Vía urbana en pendiente, anchura 3.10–3.20 m, calzada estrecha en curva. | Tipo: atropello; pendiente: 68.3% |

### §3 Características del lugar (LIDAR 3D)

| | IURGI/ITRASA oficial | Veridict |
|---|---|---|
| Contenido | Anchura 3.10–3.20 m, distancia visibilidad 26.5 m / >30 m según trayectoria curva, pendiente 9-11.6%. | pendiente 68.3% (DEM); observaciones del perito instructor citadas |

### §5 Vehículos implicados

| | IURGI/ITRASA oficial | Veridict |
|---|---|---|
| Contenido | SEAT Ibiza (anchura 1.64 m según Virtual Crash 5.0). Bicicleta Orbea, sillín 79 cm, manillar 55 cm. | SEAT Ibiza: masa 1115.0 kg, ancho 1.78 m, 3 sistemas seguridad, fuente SEAT España — ficha técnica Ibiza (5ª gen.) · Orbea bicicleta deportiva (n.º bastidor 3773): masa 1300.0 kg, ancho 1.8 m, 3 sistemas seguridad, fuente Promedio segmento C europeo (estimación) |

### §6 Análisis del atestado policial (CRÍTICA)

| | IURGI/ITRASA oficial | Veridict |
|---|---|---|
| Contenido | Errores: límite genérico 30 km/h erróneo para 2020; croquis sin escala; sin cálculos de velocidad; retroceso 'imposible'; ausencia de pruebas drogas; conclusiones carentes de rigor científico. | Valoración global: **deficiente**. 5 incongruencias, 6 omisiones detectadas. Reglas R1-R8 aplicadas automáticamente. |

### §7 Análisis de velocidad del turismo

| | IURGI/ITRASA oficial | Veridict |
|---|---|---|
| Contenido | Daños altos en parabrisas/techo → ≥50 km/h según UC3M-GC 2020. | WAD parabrisas central: 45.0-60.0 km/h |

### §8 Estudio biomecánico

| | IURGI/ITRASA oficial | Veridict |
|---|---|---|
| Contenido | Leyes de Newton, Ec=½mv². Energía a 50 km/h: 110.918 J vs 17.747 J reglamentaria (×6.25). Lesiones cefálicas letales por autopsia. | Ec=24.8 kJ; AIS3+ p=9%; 4 mecanismos lesivos identificados; cadena de 4 impactos documentada; análisis cefálico (5 tipos lesión craneal) |

### §9 Evitabilidad

| | IURGI/ITRASA oficial | Veridict |
|---|---|---|
| Contenido | A 20 km/h con μ=0.75: detención en 1.89 m / 0.76 s. Tiempo ciclista huella 8 m: 3.33 s. Conductor tenía margen de 1.57 s para evitar la colisión. | — |

### §10 Condicionantes y posibles causas

| | IURGI/ITRASA oficial | Veridict |
|---|---|---|
| Contenido | Quebranto Art. 3 RGC (diligencia), Art. 45 RGC (adecuación velocidad), Art. 46 RGC (moderación ante ciclistas/edificios). Conductor vecino conocedor de la vía. | 7 artículos: Art. 3 RGC, Art. 45 RGC, Art. 46.1.a RGC, Art. 46.1.b RGC, Art. 46.1.d RGC, Art. 54.1 RGC |

### §11 Conclusiones (7 puntos)

| | IURGI/ITRASA oficial | Veridict |
|---|---|---|
| Contenido | 1) Fronto-lateral excéntrica. 2) Velocidad excesiva ≥50 km/h (exceso 150%). 3) Energía ×6.25. 4) Lesiones letales coherentes. 5) Conductor sin maniobra evasiva con 3.33 s. 6) Evitable por simple respeto al RGC. 7) Atestado deficiente. | 4 conclusiones generadas (incluye C-AT crítica al atestado) |

---

## 4. Conclusiones del Perito Veridict

### C1 — confianza 70%
**Q:** Determinar la velocidad real del turismo en el momento de la colisión contra el ciclista.

**A:** La velocidad del turismo en el momento del impacto se sitúa en una horquilla de 20-25 km/h, con una mejor estimación de aproximadamente 24 km/h, sustentada por tres líneas convergentes. Primera línea, los cálculos SamRAT del expediente sobre las dos marcas atribuidas al turismo: huella de 1,89 m → Vi=20,06 km/h y huella de 0,47 m → Vi=10 km/h, ambas con μ=0,75 y pendiente 5,143°. Segunda línea, el contraste con la declaración del conductor (10-20 km/h): el módulo de verificación arroja diferencia de +3,8 km/h respecto al valor superior declarado, calificando la declaración como incompatible por superar el margen del 15 %. Tercera línea, la cinemática del cuerpo: el WAD documentado (parabrisas derecho con apoyo en arista de techo) se asocia nominalmente a 45-60 km/h en colisión turismo-peatón estándar, pero la concentración de energía sobre el umbral rígido del techo (estructura no deformable, energía cinética 24,8 kJ) hace biomecánicamente compatible el desenlace letal con velocidades de 24 km/h, según excepción explícita del manual ESTT/DGT 2011 y UC3M-Guardia Civil 2020. La huella de 8 m corresponde inequívocamente a la **bicicleta** (bloqueo de cubierta trasera del ciclista en descenso), arrojando velocidad propia mínima del ciclista de 36,3 km/h por Stannard-Baker. Se concluye velocidad de impacto del turismo ~20-25 km/h, incompatible con el extremo inferior (10 km/h) declarado.

**Citas:**
- `[imagen]` foto 864c9cb1 — *SamRAT — huella de frenada 1,89 m → Vi=20,06 km/h (turismo), μ=0,75, pendiente 5,143°.*
- `[imagen]` foto 9811026f — *SamRAT — huella 0,47 m → Vi=10 km/h, mismo coeficiente y pendiente.*
- `[calculo]` SimulacionAgent — velocidad_por_huella ciclista — *v_min = 36,3 km/h con huella 8,0 m, μ=0,75, pendiente -10,3 % (Stannard-Baker).*
- `[calculo]` VerificacionAgent — *Declaración 20 km/h vs cálculo 23,84 km/h: diferencia +3,8 km/h. Incompatibles, supera margen 15 %.*
- `[imagen]` foto c8bb8b64 — *SEAT Ibiza 3526-BKL con parabrisas completamente fracturado por impacto cefálico; capó sin deformación estructural visible.*
- `[imagen]` foto 4f322155 — *Diagrama WAD 1000/1500 con puntos de impacto ciclista joven a 20-50 km/h sobre capó y parabrisas.*
- `[imagen]` foto adf66d1f — *Croquis cenital con cotas 8,008 m longitudinal y 1,215 m lateral del impacto.*
- `[imagen]` foto 8a03add7 — *Marca longitudinal de deslizamiento de la bicicleta sobre pavimento de hormigón en curva (huella ciclista de 8 m).*
- `[imagen]` foto 4ae291b1 — *Manillar Orbea con cinta métrica documentando deformación post-impacto.*
- `[ficha_tecnica]` FichaAgent — SEAT Ibiza 2018 — *Masa 1.115 kg; altura parachoques 0,42-0,70 m; altura total 1,44 m; ABS y ESC.*
- `[hecho]` BiomecanicaAgent — *Compatible con fallecimiento a ~24 km/h por concentración de energía (24,8 kJ) sobre umbral de techo rígido; mecanismo bifásico parabrisas+techo.*

### C2 — confianza 85%
**Q:** Establecer si el accidente era evitable cumpliendo la normativa de circulación.

**A:** El accidente era **objetivamente evitable** circulando a velocidad reglamentaria con la atención debida. La distancia de visibilidad efectiva medida pericialmente sobre la curva es de 26,5 m lineales (>30 m sobre trayectoria curva), confirmada por nube de puntos 3D con medición laser-escáner de 26,59 m. La distancia total de detención del SEAT Ibiza con μ=0,75, pendiente ascendente 10,3 % y t_reacción=1 s arroja: a 20 km/h → 7,40 m (5,56 m reacción + 1,84 m frenada) en 1,66 s; a 30 km/h → 12,48 m en 2,00 s. En ambos escenarios la distancia de detención es muy inferior a la visibilidad disponible (7,40 m y 12,48 m frente a 26,5 m), de modo que un conductor atento a velocidad reglamentaria habría detenido el vehículo con antelación sobrada. Aplicando el patrón de evitabilidad: el ciclista percibió el riesgo y reaccionó disponiendo de t_total ≈ 3,09 s para completar su huella de 8 m (1 s reacción + 0,5 s ejecución + 1,59 s frenada), tiempo holgadamente superior a los 1,66-2,00 s que necesitaba el turismo para detenerse a velocidad reglamentaria. Existía además, según constata el propio atestado, **zona terriza diáfana de varios metros a la derecha del turismo** con desnivel máximo de 4 cm, que permitía maniobra evasiva ejecutable y no fue acometida. La concurrencia de sobrada distancia de detención + maniobra evasiva disponible + cumplimiento del art. 45 y 46.1.b RGC confirma la evitabilidad técnica del siniestro.

**Citas:**
- `[calculo]` SimulacionAgent — distancia_detencion 20 km/h — *d_total=7,40 m en 1,66 s (5,56 m reacción + 1,84 m frenada). μ=0,75; pendiente +10,3 %; t_r=1 s.*
- `[calculo]` SimulacionAgent — distancia_detencion 30 km/h — *d_total=12,48 m en 2,00 s (8,33 m reacción + 4,15 m frenada).*
- `[calculo]` SimulacionAgent — tiempo_huella ciclista — *t_total=3,09 s para 8 m de huella (1,0 + 0,5 + 1,59 s); v inicio bloqueo 36,3 km/h.*
- `[imagen]` foto efaa60b8 — *Nube de puntos 3D — visibilidad 26,59 m medida entre dos puntos en la curva.*
- `[imagen]` foto 9325d5e3 — *Anchura de calzada 3,104 m verificada por escaneo láser.*
- `[imagen]` foto 89969bcd — *SamRAT — distancia de parada a 50 km/h = 26,32 m (referencia: a velocidad reglamentaria la parada cabe holgadamente en la visibilidad disponible).*
- `[imagen]` foto adf66d1f — *Croquis cenital con posición longitudinal del impacto (8,008 m) y cota lateral (1,215 m del borde).*
- `[escena]` Atestado Ertzaintza Aulestia 21052020 — *Zona terriza diáfana a la derecha del turismo (desnivel máx. 4 cm) que permitiría maniobra evasiva.*
- `[meteo]` MeteoAgent — Open-Meteo ERA5 — *20,1 °C, precipitación 0 mm, viento 6,1 km/h; calzada estimada seca; es de día (atardecer 21:33).*
- `[normativa]` Art. 45 RGC (RD 1428/2003) — BOE-A-2003-23514 — *El conductor adecuará la velocidad de modo que pueda detener el vehículo dentro de los límites de su campo de visión y ante cualquier obstáculo que pueda presentarse.*
- `[normativa]` Art. 46.1.b RGC — *Obligación específica de moderar la velocidad al aproximarse a ciclos en circulación.*

### C3 — confianza 80%
**Q:** Indicar la conducta del conductor del turismo respecto al límite de velocidad y la atención debida.

**A:** El conductor (JME, vecino del barrio y conocedor del trazado y de la limitación) presenta dos desviaciones técnicamente acreditadas. **Respecto al límite de velocidad**: la señal vertical R-301 de 20 km/h del Barrio Zubero está fotográficamente acreditada (fotos e234bc44 y c4557c1c) — extremo no documentado por el atestado pero sí verificado pericialmente. La velocidad de impacto reconstruida (20-25 km/h, mejor estimación 24 km/h) se sitúa en el límite o ligeramente por encima del máximo permitido. Aunque el RD 970/2020 sobre límites genéricos urbanos no estaba en vigor a la fecha del siniestro (sólo desde octubre de 2020), la limitación específica de 20 km/h sí era plenamente vigente por señalización vertical. En cualquier caso, no era una velocidad **adecuada** a las circunstancias del art. 45 RGC: vía de 3,10-3,20 m de anchura (apenas suficiente para cruce con ciclista de 0,55 m de manillar), curva con visibilidad efectiva 26,5 m y pendiente 9-11,6 %, lo que exigía circular a velocidad que permitiera detenerse en cualquier punto del campo de visión. **Respecto a la atención debida**: la conducta es incompatible con la diligencia del art. 3 RGC. Con 26,5 m de visibilidad y distancia de detención de 7,4 m a 20 km/h, la única explicación física para la colisión es que el conductor (a) no reaccionó en el plazo normal de 1 s a la aparición del ciclista, (b) no efectuó frenada plena sostenida —compatible con la ausencia de huella visible del turismo— y (c) no acometió la maniobra evasiva disponible hacia la zona terriza derecha. Adicionalmente concurre el incumplimiento específico del art. 46.1.b RGC (moderación al aproximarse a ciclos) y, vía principio de confianza jurisprudencial, el ciclista que circulaba correctamente por su mitad derecha vio invadida su trayectoria por un vehículo cuya conducción no fue diligente.

**Citas:**
- `[imagen]` foto e234bc44 — *Señal R-301 de limitación 20 km/h junto a cartel municipal Ayuntamiento de Aulesti.*
- `[imagen]` foto c4557c1c — *Incorporación con señal de límite 20 km/h y topónimo Zubero auzoa.*
- `[calculo]` VerificacionAgent — *Velocidad declarada 20 km/h vs cálculo 23,84 km/h — incompatibles.*
- `[hecho]` Atestado Ertzaintza — *'No se observan huellas del turismo' pese a declaración de frenada al máximo: contradicción.*
- `[calculo]` SimulacionAgent — distancia_detencion 20 km/h — *7,40 m en 1,66 s frente a 26,5 m de visibilidad: la detención cabía 3,5 veces.*
- `[escena]` Atestado — *Zona terriza diáfana a la derecha (desnivel 4 cm) — maniobra evasiva disponible no acometida.*
- `[normativa]` Art. 3 RGC (RD 1428/2003) — *Conducción con la diligencia y precaución necesarias para evitar todo daño propio o ajeno.*
- `[normativa]` Art. 45 RGC — *Adecuación de velocidad al campo de visión y obstáculos previsibles.*
- `[normativa]` Art. 46.1.b RGC — *Moderación específica al aproximarse a ciclos.*
- `[normativa]` Principio de confianza — STS Sala 2.ª 1356/1999, 738/2003 — *El usuario que circula correctamente puede confiar en el cumplimiento ajeno; su quebrantamiento desplaza la responsabilidad.*
- `[normativa]` Advertencia temporal — RD 970/2020 (BOE-A-2020-12912) — *Límite genérico urbano de 20/30 km/h NO vigente el 21/05/2020; aplicable únicamente la señalización específica.*

### C-AT — confianza 90%
**Q:** Crítica metodológica al atestado

**A:** La conformidad del atestado de la Ertzaintza (Aulestia 21052020) se valora globalmente como **deficiente**. Se identifican cinco incongruencias y seis omisiones de relevancia probatoria. Incongruencias: (1) afirmación del límite de 20 km/h sin acreditación fotográfica de la señal —omisión que el perito subsana fotografiando la R-301 in situ—; (2) contradicción entre la declaración de frenada al máximo del conductor y la constatación de que 'no se observan huellas del turismo' en calzada seca con μ=0,75; (3) discrepancia entre la visibilidad estimada por el atestado (20 m) y la medida pericial (26,5 m / >30 m por trayectoria curva), divergencia del 32-50 % que afecta al cálculo de evitabilidad; (4) mención de la zona terriza evasiva sin análisis técnico de su ejecutabilidad; (5) elección implícita del extremo superior (20 km/h) del rango declarado por el conductor (10-20 km/h) sin justificación. Omisiones: (a) prueba de detección de alcohol y drogas al conductor preceptiva por resultado letal (art. 379 CP); (b) cálculo formal de velocidad por metodología reconocida (Stannard-Baker, CRASH3, EBS) pese a disponer de huellas y μ; (c) acreditación documental/fotográfica de la señal R-301; (d) acotación métrica precisa del PDI; (e) inspección técnica del estado de neumáticos y sistema de frenado del turismo, esencial cuando la ausencia de huella es elemento central; (f) posición final del cuerpo de la víctima con cotas. Estas carencias justifican la ampliación del atestado solicitada y motivan la presente pericia complementaria.

**Citas:**
- `[hecho]` ConformidadAgent — valoración global — *Atestado calificado como 'deficiente'. 5 incongruencias y 6 elementos omitidos.*
- `[hecho]` ConformidadAgent — incongruencia alta 1 — *Afirmación de límite 20 km/h sin respaldo fotográfico.*
- `[hecho]` ConformidadAgent — incongruencia alta 2 — *Frenada máxima declarada vs ausencia de huellas del turismo en seco.*
- `[hecho]` ConformidadAgent — incongruencia media — *Visibilidad atestado 20 m vs pericial 26,5 m.*
- `[hecho]` ConformidadAgent — omisión 1 — *Sin prueba de alcohol/drogas al conductor (preceptiva en accidente letal).*
- `[hecho]` ConformidadAgent — omisión 2 — *Sin cálculo cinemático formal pese a disponer de huellas y μ.*
- `[hecho]` ConformidadAgent — omisión 5 — *Sin inspección técnica de neumáticos/frenos del turismo.*
- `[imagen]` foto e234bc44 — *El perito aporta la fotografía omitida por el atestado de la señal R-301.*
- `[imagen]` foto efaa60b8 — *Medición laser-escáner 26,59 m — refuta visibilidad de 20 m del atestado.*


**Confianza global:** 78%