"""RAG retrieval from Qdrant vector database."""

from typing import Optional
from config import get_settings


async def search_legal_corpus(
    query: str,
    collection: Optional[str] = None,
    limit: int = 5,
    filters: Optional[dict] = None,
) -> list[dict]:
    """
    Search the legal corpus using semantic search.

    Args:
        query: Search query
        collection: Qdrant collection name
        limit: Max results
        filters: Optional metadata filters

    Returns:
        List of relevant documents
    """
    settings = get_settings()
    collection = collection or settings.qdrant_collection

    if not settings.qdrant_url:
        return _get_mock_results(query)

    # In production, would:
    # 1. Generate embedding for query
    # 2. Search Qdrant
    # 3. Return results with metadata

    return _get_mock_results(query)


def _get_mock_results(query: str) -> list[dict]:
    """Return mock search results."""
    query_lower = query.lower()

    results = []

    if "velocidad" in query_lower or "exceso" in query_lower:
        results.append({
            "content": "Articulo 74.1 RGC: Todo conductor esta obligado a respetar los limites de velocidad establecidos...",
            "metadata": {
                "source": "BOE-A-2003-23514",
                "article": "74.1",
                "title": "Reglamento General de Circulacion",
            },
            "score": 0.92,
        })

    if "distancia" in query_lower or "seguridad" in query_lower:
        results.append({
            "content": "Articulo 54.1 RGC: Todo conductor debera mantener la distancia de seguridad respecto del vehiculo que le preceda...",
            "metadata": {
                "source": "BOE-A-2003-23514",
                "article": "54.1",
                "title": "Reglamento General de Circulacion",
            },
            "score": 0.89,
        })

    if "peaton" in query_lower or "paso" in query_lower:
        results.append({
            "content": "Articulo 65.3.a LSV: Los conductores tienen obligacion de dar preferencia de paso a los peatones en los pasos senalizados...",
            "metadata": {
                "source": "BOE-A-2015-11722",
                "article": "65.3.a",
                "title": "Ley sobre Trafico",
            },
            "score": 0.88,
        })

    if "cambio" in query_lower or "carril" in query_lower:
        results.append({
            "content": "Articulo 72.1 RGC: El conductor que pretenda efectuar un desplazamiento lateral lo advertira con suficiente antelacion...",
            "metadata": {
                "source": "BOE-A-2003-23514",
                "article": "72.1",
                "title": "Reglamento General de Circulacion",
            },
            "score": 0.87,
        })

    return results or [{
        "content": "No se encontraron articulos relevantes",
        "metadata": {"source": "mock"},
        "score": 0.0,
    }]
