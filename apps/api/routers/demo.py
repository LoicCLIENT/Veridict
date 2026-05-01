"""Router for demo operations."""

from datetime import datetime
from fastapi import APIRouter, HTTPException

from models import (
    Caso,
    EstadoCaso,
    TipoColision,
    Ubicacion,
    Vehiculo,
    Resultado,
    Evento,
    CalculoFisico,
    Infraccion,
    Veredicto,
    CompatibilidadVersiones,
)
from routers.casos import casos_db

router = APIRouter()


def init_demo_casos():
    """Initialize demo cases."""
    # Caso 1: Cambio de carril M-30
    caso1 = Caso(
        id="demo-1",
        estado=EstadoCaso.COMPLETADO,
        fecha_accidente=datetime(2026, 4, 15, 14, 30),
        ubicacion=Ubicacion(lat=40.4168, lon=-3.7038),
        tipo_colision=TipoColision.LATERAL,
        vehiculos=[
            Vehiculo(
                id="A",
                matricula="1234 ABC",
                modelo="Seat Leon 2020",
                masa_kg=1350,
                mediciones_C=[12.5, 15.2, 18.3, 16.1, 14.0, 11.2],
                ancho_zona_danada_cm=85,
                version_conductor="Circulaba a 50 km/h cuando el otro vehiculo invadio mi carril",
            ),
            Vehiculo(
                id="B",
                matricula="5678 DEF",
                modelo="Volkswagen Golf 2019",
                masa_kg=1400,
                mediciones_C=[8.2, 11.5, 14.1, 12.3, 9.8, 7.5],
                ancho_zona_danada_cm=65,
                version_conductor="Estaba cambiando de carril correctamente cuando me golpearon",
            ),
        ],
        resultado=Resultado(
            cronologia=[
                Evento(timestamp=0, descripcion="Vehiculo A circula por carril derecho a 67 km/h"),
                Evento(timestamp=2, descripcion="Vehiculo B inicia cambio de carril sin senalizar"),
                Evento(timestamp=3, descripcion="Vehiculo A detecta peligro e inicia frenada"),
                Evento(timestamp=4, descripcion="Colision lateral en zona delantera derecha"),
            ],
            calculos=[
                CalculoFisico(
                    nombre="Velocidad pre-frenada (Stannard Baker)",
                    formula="V = sqrt(2 * mu * g * d)",
                    valor=67.3,
                    unidad="km/h",
                    justificacion="Huella de frenada de 12.5m, mu=0.65 (asfalto mojado)",
                ),
                CalculoFisico(
                    nombre="EBS por deformacion (CRASH3)",
                    formula="EBS = sqrt((A*C + B*C^2/2) / m)",
                    valor=45.2,
                    unidad="km/h",
                    justificacion="Deformacion media 14.5cm, coeficientes NHTSA para Seat Leon",
                ),
            ],
            infracciones=[
                Infraccion(
                    articulo="Art. 74.1 RGC",
                    descripcion="Circular a velocidad superior a la permitida (67 km/h en zona 50)",
                    vehiculo="A",
                    fuente="BOE-A-2003-23514",
                ),
                Infraccion(
                    articulo="Art. 72.1 RGC",
                    descripcion="Cambio de carril sin senalizar la maniobra con suficiente antelacion",
                    vehiculo="B",
                    fuente="BOE-A-2003-23514",
                ),
            ],
            veredicto=Veredicto(culpa_a=0.65, culpa_b=0.35, confidence=0.89),
            compatibilidad_versiones=CompatibilidadVersiones(
                a=False,
                b=False,
                justificacion="Version A incompatible: deformaciones indican 67 km/h no 50 km/h. Version B incompatible: no hay evidencia de uso de intermitente.",
            ),
            devils_advocate_passed=True,
            sigstore_hash="sha256:a1b2c3d4e5f6...",
        ),
    )

    # Caso 2: Atropello Alcala
    caso2 = Caso(
        id="demo-2",
        estado=EstadoCaso.COMPLETADO,
        fecha_accidente=datetime(2026, 4, 20, 9, 15),
        ubicacion=Ubicacion(lat=40.4825, lon=-3.3645),
        tipo_colision=TipoColision.ATROPELLO,
        vehiculos=[
            Vehiculo(
                id="A",
                matricula="9012 GHI",
                modelo="Renault Clio 2021",
                masa_kg=1200,
                mediciones_C=[5.5, 8.2, 10.1, 8.8, 6.2, 4.1],
                ancho_zona_danada_cm=120,
                version_conductor="Circulaba a 30 km/h, el peaton cruzo sin mirar",
            ),
        ],
        resultado=Resultado(
            cronologia=[
                Evento(timestamp=0, descripcion="Vehiculo A aproximandose a paso de cebra a 52 km/h"),
                Evento(timestamp=1.5, descripcion="Peaton inicia cruce por paso de cebra"),
                Evento(timestamp=2.2, descripcion="Conductor detecta peaton e inicia frenada"),
                Evento(timestamp=2.8, descripcion="Impacto con peaton"),
            ],
            calculos=[
                CalculoFisico(
                    nombre="Velocidad por deformacion capo",
                    formula="EBS = sqrt((A*C + B*C^2/2) / m)",
                    valor=52.1,
                    unidad="km/h",
                    justificacion="Deformacion del capo compatible con impacto peaton a 52 km/h",
                ),
                CalculoFisico(
                    nombre="Distancia proyeccion peaton",
                    formula="V = sqrt(d * g / 0.5)",
                    valor=48.5,
                    unidad="km/h",
                    justificacion="Peaton proyectado 8.2m, compatible con velocidad >45 km/h",
                ),
            ],
            infracciones=[
                Infraccion(
                    articulo="Art. 74.1 RGC",
                    descripcion="Circular a 52 km/h en zona 30",
                    vehiculo="A",
                    fuente="BOE-A-2003-23514",
                ),
                Infraccion(
                    articulo="Art. 65.3.a LSV",
                    descripcion="No respetar preferencia de paso a peaton en paso de cebra",
                    vehiculo="A",
                    fuente="BOE-A-2015-11722",
                ),
            ],
            veredicto=Veredicto(culpa_a=0.95, culpa_b=0.05, confidence=0.94),
            compatibilidad_versiones=CompatibilidadVersiones(
                a=False,
                b=True,
                justificacion="Version conductor INCOMPATIBLE: deformaciones y proyeccion demuestran velocidad de 52 km/h, no 30 km/h declarados. Diferencia de 22 km/h fisicamente imposible de explicar.",
            ),
            devils_advocate_passed=True,
            sigstore_hash="sha256:f6e5d4c3b2a1...",
        ),
    )

    # Caso 3: Alcance A-6
    caso3 = Caso(
        id="demo-3",
        estado=EstadoCaso.COMPLETADO,
        fecha_accidente=datetime(2026, 4, 22, 18, 45),
        ubicacion=Ubicacion(lat=40.4500, lon=-3.7200),
        tipo_colision=TipoColision.ALCANCE,
        vehiculos=[
            Vehiculo(
                id="A",
                matricula="3456 JKL",
                modelo="BMW Serie 3 2022",
                masa_kg=1550,
                mediciones_C=[18.5, 22.1, 25.8, 23.2, 19.5, 15.8],
                ancho_zona_danada_cm=140,
                version_conductor="El vehiculo de delante freno bruscamente sin motivo",
            ),
            Vehiculo(
                id="B",
                matricula="7890 MNO",
                modelo="Toyota Corolla 2020",
                masa_kg=1380,
                mediciones_C=[12.2, 16.5, 19.8, 17.1, 13.5, 10.2],
                ancho_zona_danada_cm=120,
                version_conductor="Frene porque habia un obstaculo en la via",
            ),
        ],
        resultado=Resultado(
            cronologia=[
                Evento(timestamp=0, descripcion="Ambos vehiculos circulan a 120 km/h, distancia 15m"),
                Evento(timestamp=0.5, descripcion="Vehiculo B detecta obstaculo e inicia frenada"),
                Evento(timestamp=1.2, descripcion="Vehiculo A detecta frenada de B e inicia frenada"),
                Evento(timestamp=1.8, descripcion="Colision trasera"),
            ],
            calculos=[
                CalculoFisico(
                    nombre="Delta-V vehiculo A (EDR)",
                    formula="Delta-V = V_pre - V_post",
                    valor=35.2,
                    unidad="km/h",
                    justificacion="Dato extraido del Event Data Recorder del BMW",
                ),
                CalculoFisico(
                    nombre="Distancia seguridad requerida",
                    formula="d = V * t_reaccion + V^2 / (2*mu*g)",
                    valor=67.5,
                    unidad="m",
                    justificacion="A 120 km/h se requieren 67.5m, vehiculo A mantenia solo 15m",
                ),
            ],
            infracciones=[
                Infraccion(
                    articulo="Art. 54.1 RGC",
                    descripcion="No mantener distancia de seguridad adecuada",
                    vehiculo="A",
                    fuente="BOE-A-2003-23514",
                ),
            ],
            veredicto=Veredicto(culpa_a=0.85, culpa_b=0.15, confidence=0.92),
            compatibilidad_versiones=CompatibilidadVersiones(
                a=True,
                b=True,
                justificacion="Ambas versiones compatibles con evidencia EDR. B freno por obstaculo legitimo, A no mantenia distancia.",
            ),
            devils_advocate_passed=True,
            sigstore_hash="sha256:1a2b3c4d5e6f...",
        ),
    )

    # Add to database
    casos_db["demo-1"] = caso1
    casos_db["demo-2"] = caso2
    casos_db["demo-3"] = caso3


# Initialize on module load
init_demo_casos()


@router.get("/casos", response_model=list[Caso])
async def listar_demo_casos() -> list[Caso]:
    """List pre-loaded demo cases."""
    return [caso for caso in casos_db.values() if caso.id.startswith("demo-")]


@router.post("/casos/{caso_id}/reset")
async def reset_demo_caso(caso_id: str) -> dict:
    """Reset a demo case to initial state."""
    if not caso_id.startswith("demo-"):
        raise HTTPException(status_code=400, detail="Only demo cases can be reset")

    # Re-initialize demo cases
    init_demo_casos()

    return {"status": "reset", "caso_id": caso_id}
