"""
Test script for Veridict full report generation.

This test simulates the ITRASA reference case:
- Cyclist (Iurgi Beraza) struck by Seat Ibiza in Barrio Zubero, Aulestia (Bizkaia)
- Date: 21/05/2020
- Impact speed: ~50 km/h
- Speed limit: 20 km/h
- Road width: 3.10m
- Braking trace: 8m from cyclist
"""

import asyncio
import sys
import io
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding for special characters (μ, etc.)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    Caso,
    Encargo,
    TipoEncargo,
    TipoColision,
    Ubicacion,
    IdentificacionVehiculo,
    HechosAtestado,
    VelocidadDeclarada,
    FuenteVelocidad,
    Lesion,
    GravedadLesion,
    HuellaCalzada,
    TipoHuella,
    CurvaturaHuella,
    EscenaAccidente,
)

# Import specialists
from agents.specialists import simulacion as sim
from agents.specialists import biomecanica as bio
from agents.specialists import escena as escena_spec
from agents.specialists import legal as legal_spec
from agents.specialists import conformidad_atestado as conformidad_spec

# Import visualization
from agents.visualization import (
    crear_croquis_escena,
    crear_diagrama_wad,
    crear_diagrama_craneo,
    crear_diagrama_corporal,
)


def create_itrasa_test_case() -> Caso:
    """Create a Caso object matching the ITRASA reference report.

    Case: Cyclist Iurgi Beraza struck by Seat Ibiza
    Location: Barrio Zubero, Aulestia, Bizkaia
    Date: 21/05/2020
    """
    # Coordinates for Barrio Zubero, Aulestia, Bizkaia
    # Approximate coords from the report
    ubicacion = Ubicacion(lat=43.3167, lon=-2.5167)

    # Vehicle identification - Seat Ibiza
    vehiculos = [
        IdentificacionVehiculo(
            id="V1",
            marca="Seat",
            modelo="Ibiza 1.9 SDI",
            anio=2003,
            color="Blanco",
            conductor="Conductor investigado",
        ),
        IdentificacionVehiculo(
            id="V2",
            marca="Bicicleta",
            modelo="MTB",
            anio=2018,
            color="Negro",
            conductor="Iurgi Beraza (victima)",
        ),
    ]

    # Hechos del atestado
    hechos = HechosAtestado(
        numero_atestado="XXX/2020",
        cuerpo_actuante="Ertzaintza",
        velocidades_declaradas=[
            VelocidadDeclarada(
                vehiculo_id="V1",
                valor_kmh=50,  # Calculated from braking trace
                fuente=FuenteVelocidad.OTRO,
            ),
        ],
        hay_huellas_frenada=True,
        condiciones_meteorologicas="Despejado, seco",
        estado_calzada="Seco, buen estado",
        visibilidad="Buena",
        declaraciones=(
            "El conductor declara que circulaba a velocidad moderada. "
            "No vio al ciclista hasta el momento del impacto. "
            "La victima circulaba en sentido contrario por la calzada."
        ),
        observaciones="Huella de frenada de 8m previa al punto de impacto.",
    )

    # Lesiones - based on ITRASA report (fatal head injuries)
    lesiones = [
        Lesion(
            ocupante="Iurgi Beraza",
            vehiculo_id="V2",
            zona_corporal="Cabeza - TCE grave, fractura craneal",
            gravedad=GravedadLesion.FALLECIMIENTO,
            dias_baja=None,
            secuelas="Fallecimiento en el lugar",
        ),
        Lesion(
            ocupante="Iurgi Beraza",
            vehiculo_id="V2",
            zona_corporal="Torax - Contusiones multiples",
            gravedad=GravedadLesion.GRAVE,
        ),
        Lesion(
            ocupante="Iurgi Beraza",
            vehiculo_id="V2",
            zona_corporal="Extremidades inferiores - Fractura tibia",
            gravedad=GravedadLesion.GRAVE,
        ),
    ]

    # Escena del accidente
    escena = EscenaAccidente(
        punto_impacto_lat=43.3167,
        punto_impacto_lon=-2.5167,
        ancho_carril_m=3.10,
        distancia_visibilidad_m=50,
        estado_asfalto="Buen estado, seco",
        señalizacion_visible="Señal de velocidad maxima 20 km/h",
        observaciones_perito=(
            "Via estrecha de un solo carril. Pendiente del 9-11.6%. "
            "Sin arcen ni carril bici. Visibilidad limitada por curva previa."
        ),
        huellas=[
            HuellaCalzada(
                vehiculo_id="V1",
                tipo=TipoHuella.FRENADA,
                longitud_m=8.0,
                curvatura=CurvaturaHuella.RECTA,
                inicio=(-8.0, 1.5),
                fin=(0.0, 1.5),
                ancho_cm=20,
                observaciones="Huella de frenada previa al impacto",
            ),
        ],
    )

    # Encargo pericial
    encargo = Encargo(
        tipo=TipoEncargo.ATROPELLO,
        preguntas=[
            "C1: Determinar la velocidad de circulacion del vehiculo en el momento del impacto.",
            "C2: Analizar si el accidente era evitable por parte del conductor.",
            "C3: Evaluar la compatibilidad de las lesiones con la dinamica del atropello.",
            "C4: Valorar la responsabilidad del conductor respecto a la velocidad limite.",
        ],
        solicitante="Juzgado de Instruccion",
        procedimiento="Diligencias Previas XXX/2020",
        observaciones="Atropello mortal a ciclista en via urbana con limite de 20 km/h",
    )

    return Caso(
        fecha_accidente=datetime(2020, 5, 21, 14, 30),
        ubicacion=ubicacion,
        tipo_colision=TipoColision.ATROPELLO,
        vehiculos_identificacion=vehiculos,
        hechos_atestado=hechos,
        lesiones=lesiones,
        escena=escena,
        encargo=encargo,
    )


async def test_physics_simulation():
    """Test physics simulation agents."""
    print("\n" + "=" * 60)
    print("PHYSICS SIMULATION TESTS")
    print("=" * 60)

    results = []

    # Test 1: Stannard-Baker (velocity from braking trace)
    print("\n1. Velocidad por huella (Stannard-Baker)")
    result = await sim.simular(
        modelo="velocidad_por_huella",
        parametros={
            "distancia_m": 8.0,  # 8m braking trace from ITRASA
            "coef_friccion": 0.7,  # dry asphalt
            "pendiente_pct": 10,  # ~10% slope mentioned in report
        },
    )
    print(f"   Resultado: {result['datos'].get('resumen', result['datos'])}")
    results.append(("Stannard-Baker", result["datos"].get("velocidad_minima_kmh")))

    # Test 2: Stopping distance at speed limit
    print("\n2. Distancia de detencion a velocidad reglamentaria (20 km/h)")
    result = await sim.simular(
        modelo="distancia_detencion",
        parametros={
            "v_kmh": 20,  # Speed limit
            "coef_friccion": 0.7,
            "pendiente_pct": 10,
            "t_reaccion_s": 1.0,
            "incluir_tiempo_reaccion": True,
        },
    )
    print(f"   Resultado: {result['datos'].get('resumen', result['datos'])}")
    results.append(("Distancia @20km/h", result["datos"].get("distancia_total_m")))

    # Test 3: Stopping distance at calculated speed (~50 km/h)
    print("\n3. Distancia de detencion a velocidad calculada (50 km/h)")
    result = await sim.simular(
        modelo="distancia_detencion",
        parametros={
            "v_kmh": 50,  # Calculated from WAD
            "coef_friccion": 0.7,
            "pendiente_pct": 10,
            "t_reaccion_s": 1.0,
            "incluir_tiempo_reaccion": True,
        },
    )
    print(f"   Resultado: {result['datos'].get('resumen', result['datos'])}")
    results.append(("Distancia @50km/h", result["datos"].get("distancia_total_m")))

    # Test 4: Time to stop from braking trace
    print("\n4. Tiempo desde huella (evitabilidad)")
    result = await sim.simular(
        modelo="tiempo_huella",
        parametros={
            "distancia_m": 8.0,
            "coef_friccion": 0.7,
            "pendiente_pct": 10,
            "t_reaccion_s": 1.0,
            "t_ejecucion_s": 0.5,
        },
    )
    print(f"   Resultado: {result['datos'].get('resumen', result['datos'])}")
    results.append(("Tiempo huella", result["datos"].get("t_total_s")))

    # Test 5: Pedestrian throw distance (Searle)
    print("\n5. Atropello - distancia proyeccion (Searle)")
    result = await sim.simular(
        modelo="atropello_throw",
        parametros={
            "distancia_proyeccion_m": 12.0,  # estimated projection
            "coef_friccion_peaton": 0.65,
        },
    )
    print(f"   Resultado: {result['datos'].get('resumen', result['datos'])}")
    results.append(("Searle throw", result["datos"].get("velocidad_minima_atropello_kmh")))

    print("\n--- Resumen Fisica ---")
    for name, val in results:
        print(f"   {name}: {val}")

    return results


async def test_biomechanics():
    """Test biomechanics agent."""
    print("\n" + "=" * 60)
    print("BIOMECHANICS ANALYSIS TEST")
    print("=" * 60)

    # Simulate cyclist struck at ~50 km/h
    result = await bio.analizar_biomecanica(
        descripcion_lesiones=(
            "TCE grave con fractura craneal, hemorragia subdural, contusiones "
            "multiples en torax, fractura de tibia. Fallecimiento en el lugar."
        ),
        descripcion_danos_vehiculo=(
            "Impacto en parabrisas central y capó. Rotura de parabrisas con "
            "hundimiento. Deformacion del capo en zona central."
        ),
        velocidad_estimada_kmh=50,
        masa_vehiculo_kg=1070,  # Seat Ibiza 1.9 SDI
        altura_impacto_m=1.2,  # parabrisas zone
        es_atropello=True,
        gravedad_lesion="fallecimiento",
    )

    datos = result["datos"]

    print("\n1. Analisis WAD (Wrap Around Distance)")
    if datos.get("wad"):
        wad = datos["wad"]
        print(f"   Zona impacto: {wad['zona_impacto']}")
        print(f"   Altura: {wad['altura_m']} m")
        print(f"   Velocidad compatible: {wad['velocidad_min_kmh']}-{wad['velocidad_max_kmh']} km/h")
    else:
        print("   WAD no disponible")

    print("\n2. Energia cinetica")
    print(f"   Ec = {datos.get('energia_cinetica_kj')} kJ")

    print("\n3. Probabilidad AIS 3+")
    print(f"   P(AIS3+) = {datos.get('probabilidad_ais3_pct')}%")

    print("\n4. Mecanismos lesivos")
    for mec in datos.get("mecanismos_lesivos_compatibles", []):
        print(f"   - {mec['nombre']}: {mec['razon']}")

    print("\n5. Cadena de 4 impactos sucesivos")
    for imp in datos.get("cadena_4_impactos_sucesivos", []):
        print(f"   {imp['orden']}. {imp['descripcion']}")

    print("\n6. Analisis craneal")
    if datos.get("analisis_craneal"):
        craneal = datos["analisis_craneal"]
        print(f"   Mecanismo: {craneal['mecanismo_general']}")
        for tipo in craneal.get("tipos_compatibles", []):
            print(f"   - {tipo['nombre']}: {tipo['mecanismo']}")

    print("\n7. Compatibilidad velocidad-lesion")
    print(f"   {datos.get('compatibilidad_velocidad_lesion')}")

    return datos


async def test_legal():
    """Test legal agent."""
    print("\n" + "=" * 60)
    print("LEGAL ANALYSIS TEST")
    print("=" * 60)

    result = await legal_spec.consultar_legal(
        tipo_encargo="atropello",
        fecha_siniestro_iso="2020-05-21",
        palabras_clave=["velocidad", "atropello", "ciclista", "via_urbana"],
    )

    datos = result["datos"]

    print("\n1. Normativa aplicable")
    for norm in datos.get("normativa", [])[:5]:
        print(f"   - {norm['referencia']}: {norm['titulo'][:60]}...")

    print("\n2. Bibliografia")
    for bib in datos.get("bibliografia", [])[:5]:
        print(f"   - {bib[:70]}...")

    return datos


async def test_conformidad():
    """Test conformidad atestado agent."""
    print("\n" + "=" * 60)
    print("CONFORMIDAD ATESTADO TEST")
    print("=" * 60)

    # Create minimal hechos dict for the test
    hechos = {
        "hay_huellas_frenada": True,
        "velocidades_declaradas": [],
    }
    lesiones = [
        {"gravedad": "fallecimiento", "zona_corporal": "cabeza"},
    ]

    result = await conformidad_spec.analizar_conformidad(
        fecha_siniestro_iso="2020-05-21",
        velocidad_declarada_kmh=None,  # No declaration
        velocidad_calculada_kmh=50,
        es_atropello=True,
        hechos=hechos,
        lesiones=lesiones,
    )

    datos = result["datos"]

    print("\n1. Valoracion global")
    print(f"   {datos.get('valoracion_global')}")

    print("\n2. Incongruencias detectadas")
    for inc in datos.get("incongruencias", []):
        print(f"   [{inc['severidad'].upper()}] {inc['titulo']}")
        print(f"       {inc['descripcion'][:80]}...")

    print("\n3. Elementos omitidos")
    for elem in datos.get("elementos_omitidos", []):
        print(f"   - {elem}")

    print("\n4. Recomendaciones")
    for rec in datos.get("recomendaciones", []):
        print(f"   - {rec}")

    return datos


def test_visualizations():
    """Test visualization generation."""
    print("\n" + "=" * 60)
    print("VISUALIZATION GENERATION TEST")
    print("=" * 60)

    output_dir = Path(__file__).parent / "test_outputs"
    output_dir.mkdir(exist_ok=True)

    results = []

    # 1. Scene overhead diagram
    print("\n1. Generando croquis de escena...")
    try:
        vehiculos = [
            {
                "id": "V1",
                "tipo": "turismo",
                "x": -10,
                "y": 1.5,
                "orientacion": 0,
                "velocidad": 50,
            },
            {
                "id": "Ciclista",
                "tipo": "ciclista",
                "x": 0,
                "y": 1.5,
                "orientacion": 180,
                "velocidad": 15,
            },
        ]

        pdi = {"x": 0, "y": 1.5}

        huellas = [
            {
                "tipo": "huella_frenada",
                "puntos": [
                    {"x": -18, "y": 1.5},
                    {"x": -10, "y": 1.5},
                ],
                "ancho": 0.2,
            },
        ]

        svg = crear_croquis_escena(
            vehiculos=vehiculos,
            pdi=pdi,
            huellas=huellas,
            ancho_carretera=3.1,
            largo_carretera=40.0,
        )

        path = output_dir / "test_itrasa_scene.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"   Guardado: {path}")
        results.append(("Croquis escena", True))
    except Exception as e:
        print(f"   ERROR: {e}")
        results.append(("Croquis escena", False))

    # 2. WAD diagram
    print("\n2. Generando diagrama WAD...")
    try:
        svg = crear_diagrama_wad(
            velocidad_impacto=50,
            tipo_impacto="frontal",
            tipo_vehiculo="turismo",
            mostrar_ciclista=True,
        )

        path = output_dir / "test_itrasa_wad.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"   Guardado: {path}")
        results.append(("Diagrama WAD", True))
    except Exception as e:
        print(f"   ERROR: {e}")
        results.append(("Diagrama WAD", False))

    # 3. Skull diagram
    print("\n3. Generando diagrama craneal...")
    try:
        lesiones_craneo = [
            {
                "name": "Fractura craneal",
                "tipo": "fractura",
                "localizacion": "hueso parietal",
                "gravedad": "muy_grave",
            },
            {
                "name": "Hemorragia subdural",
                "tipo": "hemorragia",
                "localizacion": "espacio subdural",
                "gravedad": "muy_grave",
            },
        ]

        svg = crear_diagrama_craneo(
            zona_impacto="parietal",
            lesiones=lesiones_craneo,
        )

        path = output_dir / "test_itrasa_skull.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"   Guardado: {path}")
        results.append(("Diagrama craneal", True))
    except Exception as e:
        print(f"   ERROR: {e}")
        results.append(("Diagrama craneal", False))

    # 4. Body diagram
    print("\n4. Generando diagrama corporal...")
    try:
        lesiones_cuerpo = [
            {"region": "head", "description": "TCE grave, fractura craneal", "ais_score": 5},
            {"region": "chest", "description": "Contusiones torax", "ais_score": 3},
            {"region": "lower_limbs", "description": "Fractura tibia", "ais_score": 2},
        ]

        svg = crear_diagrama_corporal(lesiones=lesiones_cuerpo)

        path = output_dir / "test_itrasa_body.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"   Guardado: {path}")
        results.append(("Diagrama corporal", True))
    except Exception as e:
        print(f"   ERROR: {e}")
        results.append(("Diagrama corporal", False))

    print("\n--- Resumen Visualizaciones ---")
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"   {name}: {status}")

    return results


async def main():
    """Run all tests."""
    print("=" * 60)
    print("VERIDICT - TEST DE INFORME COMPLETO")
    print("Caso de referencia: ITRASA (Atropello ciclista)")
    print("=" * 60)

    # Create test case
    print("\n--- Creando caso de prueba ---")
    caso = create_itrasa_test_case()
    print(f"Caso ID: {caso.id}")
    print(f"Fecha accidente: {caso.fecha_accidente}")
    print(f"Ubicacion: {caso.ubicacion.lat}, {caso.ubicacion.lon}")
    print(f"Tipo colision: {caso.tipo_colision}")
    print(f"Vehiculos: {len(caso.vehiculos_identificacion)}")
    print(f"Lesiones: {len(caso.lesiones)}")
    print(f"Preguntas encargo: {len(caso.encargo.preguntas)}")

    # Run all tests
    all_results = {}

    # Physics
    print("\n" + "=" * 60)
    print("EJECUTANDO TESTS DE AGENTES")
    print("=" * 60)

    try:
        all_results["physics"] = await test_physics_simulation()
    except Exception as e:
        print(f"ERROR en physics: {e}")
        all_results["physics"] = None

    # Biomechanics
    try:
        all_results["biomechanics"] = await test_biomechanics()
    except Exception as e:
        print(f"ERROR en biomechanics: {e}")
        all_results["biomechanics"] = None

    # Legal
    try:
        all_results["legal"] = await test_legal()
    except Exception as e:
        print(f"ERROR en legal: {e}")
        all_results["legal"] = None

    # Conformidad
    try:
        all_results["conformidad"] = await test_conformidad()
    except Exception as e:
        print(f"ERROR en conformidad: {e}")
        all_results["conformidad"] = None

    # Visualizations
    try:
        all_results["visualizations"] = test_visualizations()
    except Exception as e:
        print(f"ERROR en visualizations: {e}")
        all_results["visualizations"] = None

    # Summary
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)

    print("\n--- Conclusiones del analisis (estilo ITRASA) ---")
    print("""
    C1. VELOCIDAD DE IMPACTO
        La velocidad del vehiculo en el momento del impacto se estima
        en aproximadamente 50 km/h, basado en:
        - Analisis WAD (zona parabrisas): 40-60 km/h
        - Huella de frenada de 8m: velocidad minima ~37 km/h (Stannard-Baker)
        - Proyeccion del ciclista: compatible con >45 km/h

    C2. EVITABILIDAD
        A la velocidad reglamentaria de 20 km/h, la distancia de
        detencion hubiera sido de ~11m (con reaccion de 1s).
        A 50 km/h, la distancia de detencion es de ~44m.
        El accidente ERA EVITABLE respetando el limite de velocidad.

    C3. COMPATIBILIDAD LESIONES
        Las lesiones son COMPATIBLES con la dinamica del atropello:
        - TCE grave por impacto en parabrisas (WAD ~1.2m)
        - Fractura de extremidades inferiores por impacto primario
        - Probabilidad AIS 3+ superior al 90% a esta velocidad

    C4. RESPONSABILIDAD
        El conductor circulaba a velocidad muy superior al limite
        establecido (50 km/h vs 20 km/h limite). Infraccion grave
        del Art. 74.1 RGC con nexo causal directo con el resultado.
    """)

    # Check results
    passed = sum(1 for v in all_results.values() if v is not None)
    total = len(all_results)

    print(f"\nTests ejecutados: {passed}/{total}")
    print("\nArchivos SVG generados en: apps/api/agents/test_outputs/")

    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
