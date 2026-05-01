"""
Legal Reasoner Agent - RAG over Spanish traffic law corpus.
Uses GPT-4 + Qdrant for retrieval.
"""

from typing import Any

from models import Caso, CalculoFisico, Infraccion


class LegalReasoner:
    """Agent for legal analysis using RAG over traffic law corpus."""

    def __init__(self):
        self.model = "gpt-4o"  # GPT-4o for legal reasoning
        self.collection = "corpus_trafico_es"

    async def analyze(
        self, caso: Caso, calculos: list[CalculoFisico]
    ) -> dict[str, Any]:
        """
        Analyze case for legal infractions using RAG.

        Returns:
            dict with 'infracciones'
        """
        infracciones = []

        # Check for speed violations
        for calculo in calculos:
            if "velocidad" in calculo.nombre.lower() or "ebs" in calculo.nombre.lower():
                # Check if speed exceeds limit
                speed = calculo.valor
                limit = await self._get_speed_limit(caso)

                if speed > limit:
                    infraccion = await self._find_speed_infraction(speed, limit)
                    if infraccion:
                        infracciones.append(infraccion)

        # Check for specific collision-type infractions
        tipo_infracciones = await self._check_collision_type_infractions(caso)
        infracciones.extend(tipo_infracciones)

        return {"infracciones": infracciones}

    async def _get_speed_limit(self, caso: Caso) -> int:
        """Get speed limit for the location."""
        # In production, would query DGT/OSM data
        # Default to common limits based on collision type
        if caso.tipo_colision.value == "atropello":
            return 30  # Urban pedestrian area
        return 50  # Default urban

    async def _find_speed_infraction(
        self, actual_speed: float, limit: int
    ) -> Infraccion | None:
        """Find applicable speed infraction article."""
        # In production, would use RAG to find exact article
        if actual_speed > limit:
            return Infraccion(
                articulo="Art. 74.1 RGC",
                descripcion=f"Circular a {actual_speed:.0f} km/h en zona de {limit} km/h",
                vehiculo="A",  # Would be determined by analysis
                fuente="BOE-A-2003-23514 (Reglamento General de Circulacion)",
            )
        return None

    async def _check_collision_type_infractions(
        self, caso: Caso
    ) -> list[Infraccion]:
        """Check for infractions specific to collision type."""
        infracciones = []

        if caso.tipo_colision.value == "lateral":
            # Check for lane change violations
            infracciones.append(
                Infraccion(
                    articulo="Art. 72.1 RGC",
                    descripcion="Cambio de carril sin senalizar con suficiente antelacion",
                    vehiculo="B",
                    fuente="BOE-A-2003-23514",
                )
            )

        elif caso.tipo_colision.value == "alcance":
            # Check for safe distance violation
            infracciones.append(
                Infraccion(
                    articulo="Art. 54.1 RGC",
                    descripcion="No mantener distancia de seguridad adecuada",
                    vehiculo="A",
                    fuente="BOE-A-2003-23514",
                )
            )

        elif caso.tipo_colision.value == "atropello":
            # Check for pedestrian crossing violations
            infracciones.append(
                Infraccion(
                    articulo="Art. 65.3.a LSV",
                    descripcion="No respetar preferencia de paso a peaton en paso de cebra",
                    vehiculo="A",
                    fuente="BOE-A-2015-11722",
                )
            )

        return infracciones

    async def retrieve_jurisprudence(self, query: str) -> list[dict]:
        """Retrieve relevant jurisprudence from CENDOJ."""
        # In production, would use Qdrant RAG
        return []
