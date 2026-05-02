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
)
from routers.casos import casos_db

router = APIRouter()


def init_demo_casos():
    """Initialize demo cases."""

    # Caso 1: Colisión lateral M-30 Madrid
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
                version_conductor="Circulaba a 50 km/h cuando el otro vehículo invadió mi carril",
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
                Evento(timestamp=0, descripcion="Vehículo A circula por carril derecho a 45.6 km/h"),
                Evento(timestamp=2, descripcion="Vehículo B inicia cambio de carril sin señalizar"),
                Evento(timestamp=3, descripcion="Vehículo A detecta peligro e inicia frenada"),
                Evento(timestamp=4, descripcion="Colisión lateral en zona delantera derecha"),
            ],
            calculos=[
                CalculoFisico(
                    nombre="EBS Vehículo A (CRASH3)",
                    formula="EBS = sqrt((A·C + B·C²/2)·L / m)",
                    valor=45.6,
                    unidad="km/h",
                    justificacion="Deformación media 14.5 cm, ancho zona 85 cm, masa 1350 kg",
                ),
                CalculoFisico(
                    nombre="EBS Vehículo B (CRASH3)",
                    formula="EBS = sqrt((A·C + B·C²/2)·L / m)",
                    valor=32.4,
                    unidad="km/h",
                    justificacion="Deformación media 10.6 cm, ancho zona 65 cm, masa 1400 kg",
                ),
            ],
            infracciones=[
                Infraccion(
                    articulo="Art. 72.1 RGC",
                    descripcion="Cambio de carril sin señalizar la maniobra con suficiente antelación",
                    vehiculo="B",
                    fuente="BOE-A-2003-23514",
                ),
                Infraccion(
                    articulo="Art. 48 RGC",
                    descripcion="Invasión de carril ajeno durante maniobra de cambio sin respetar marcación vial",
                    vehiculo="B",
                    fuente="BOE-A-2003-23514",
                ),
            ],
            sigstore_hash="sha256:a1b2c3d4e5f6789a",
        ),
    )

    # Caso 2: Atropello Alcalá de Henares
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
                version_conductor="Circulaba a 30 km/h, el peatón cruzó sin mirar",
            ),
        ],
        resultado=Resultado(
            cronologia=[
                Evento(timestamp=0, descripcion="Vehículo A se aproxima a paso de cebra con EBS equivalente a 52 km/h"),
                Evento(timestamp=1.5, descripcion="Peatón inicia cruce por paso de cebra habilitado"),
                Evento(timestamp=2.2, descripcion="Conductor detecta peatón e inicia frenada"),
                Evento(timestamp=2.8, descripcion="Impacto frontal con peatón en paso de cebra"),
            ],
            calculos=[
                CalculoFisico(
                    nombre="EBS por deformación capó (CRASH3)",
                    formula="EBS = sqrt((A·C + B·C²/2)·L / m)",
                    valor=52.1,
                    unidad="km/h",
                    justificacion="Deformación capó compatible con impacto a 52 km/h. Declaración de 30 km/h no compatible.",
                ),
                CalculoFisico(
                    nombre="Velocidad por proyección de peatón",
                    formula="V = sqrt(d·g / 0.5)",
                    valor=48.5,
                    unidad="km/h",
                    justificacion="Peatón proyectado 8.2 m. Compatible con velocidad de impacto > 45 km/h.",
                ),
            ],
            infracciones=[
                Infraccion(
                    articulo="Art. 74.1 RGC",
                    descripcion="Circular a velocidad superior a la permitida: EBS calculada 52 km/h en zona limitada a 30 km/h",
                    vehiculo="A",
                    fuente="BOE-A-2003-23514",
                ),
                Infraccion(
                    articulo="Art. 65.3.a LSV",
                    descripcion="No respetar la preferencia de paso al peatón en paso de cebra habilitado",
                    vehiculo="A",
                    fuente="BOE-A-2015-11722",
                ),
            ],
            sigstore_hash="sha256:f6e5d4c3b2a19876",
        ),
    )

    # Caso 3: Alcance en A-6
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
                version_conductor="El vehículo de delante frenó bruscamente sin motivo",
            ),
            Vehiculo(
                id="B",
                matricula="7890 MNO",
                modelo="Toyota Corolla 2020",
                masa_kg=1380,
                mediciones_C=[12.2, 16.5, 19.8, 17.1, 13.5, 10.2],
                ancho_zona_danada_cm=120,
                version_conductor="Frené porque había un obstáculo en la vía",
            ),
        ],
        resultado=Resultado(
            cronologia=[
                Evento(timestamp=0, descripcion="Ambos vehículos circulan a ~120 km/h con distancia entre sí de 15 m"),
                Evento(timestamp=0.5, descripcion="Vehículo B detecta obstáculo e inicia frenada de emergencia"),
                Evento(timestamp=1.2, descripcion="Vehículo A detecta frenada de B con 0.7 s de retraso"),
                Evento(timestamp=1.8, descripcion="Colisión trasera. A impacta en zona posterior de B"),
            ],
            calculos=[
                CalculoFisico(
                    nombre="Distancia de seguridad requerida",
                    formula="d = V·t_reacción + V²/(2·μ·g)",
                    valor=67.5,
                    unidad="m",
                    justificacion="A 120 km/h se requieren 67.5 m de distancia de seguridad. A mantenía solo 15 m.",
                ),
                CalculoFisico(
                    nombre="EBS Vehículo A (CRASH3)",
                    formula="EBS = sqrt((A·C + B·C²/2)·L / m)",
                    valor=61.3,
                    unidad="km/h",
                    justificacion="Deformación frontal media 20.8 cm, ancho zona 140 cm, masa 1550 kg",
                ),
            ],
            infracciones=[
                Infraccion(
                    articulo="Art. 54.1 RGC",
                    descripcion="No mantener distancia de seguridad: 15 m real frente a 67.5 m requeridos a 120 km/h",
                    vehiculo="A",
                    fuente="BOE-A-2003-23514",
                ),
            ],
            sigstore_hash="sha256:1a2b3c4d5e6f7890",
        ),
    )

    casos_db["demo-1"] = caso1
    casos_db["demo-2"] = caso2
    casos_db["demo-3"] = caso3


init_demo_casos()


@router.get("/casos", response_model=list[Caso])
async def listar_demo_casos() -> list[Caso]:
    """Lista los casos demo precargados."""
    return [caso for caso in casos_db.values() if caso.id.startswith("demo-")]


@router.post("/casos/{caso_id}/reset")
async def reset_demo_caso(caso_id: str) -> dict:
    """Resetea un caso demo a su estado inicial."""
    if not caso_id.startswith("demo-"):
        raise HTTPException(status_code=400, detail="Solo se pueden resetear casos demo")
    init_demo_casos()
    return {"status": "reset", "caso_id": caso_id}
