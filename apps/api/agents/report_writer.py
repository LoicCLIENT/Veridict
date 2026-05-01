"""
Report Writer Agent - Generates PDF in UNE-EN 16775 format.
"""

from typing import Any

from models import Caso, Resultado


class ReportWriter:
    """Agent for generating the final PDF report."""

    def __init__(self):
        self.model = "claude-opus-4-5-20251101"

    async def generate(self, caso: Caso, resultado: Resultado) -> dict[str, Any]:
        """
        Generate PDF report and sign with Sigstore.

        Returns:
            dict with 'pdf_url' and 'sigstore_hash'
        """
        from reports.pdf_generator import generate_pdf
        from audit.sigstore_signer import sign_document

        # Generate PDF
        pdf_bytes = await generate_pdf(caso)

        # Upload to storage (mock for now)
        pdf_url = f"/api/casos/{caso.id}/pdf"

        # Sign with Sigstore
        sigstore_hash = await sign_document(pdf_bytes)

        return {
            "pdf_url": pdf_url,
            "sigstore_hash": sigstore_hash,
        }
