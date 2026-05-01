#!/usr/bin/env python3
"""
Ingest legal corpus into Qdrant vector database.
Run with: python scripts/ingest_corpus.py --source data/corpus_legal/
"""

import argparse
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "api"))


def main():
    parser = argparse.ArgumentParser(description="Ingest legal corpus into Qdrant")
    parser.add_argument(
        "--source",
        type=str,
        default="data/corpus_legal/",
        help="Source directory with PDF files",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="corpus_trafico_es",
        help="Qdrant collection name",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="Text chunk size for embeddings",
    )
    args = parser.parse_args()

    print(f"Ingesting corpus from: {args.source}")
    print(f"Target collection: {args.collection}")
    print(f"Chunk size: {args.chunk_size}")

    # Check if source directory exists
    if not os.path.exists(args.source):
        print(f"\nWARNING: Source directory '{args.source}' does not exist.")
        print("Please download the legal corpus PDFs first:")
        print("  - BOE-A-2003-23514 (Reglamento General de Circulacion)")
        print("  - BOE-A-2015-11722 (Ley sobre Trafico)")
        print("  - BOE-A-2015-10197 (Ley 35/2015 baremo)")
        print("  - BOE-A-2018-17628 (Real Decreto 1486/2018)")
        return

    # List PDF files
    pdf_files = [f for f in os.listdir(args.source) if f.endswith(".pdf")]

    if not pdf_files:
        print(f"\nNo PDF files found in {args.source}")
        return

    print(f"\nFound {len(pdf_files)} PDF files:")
    for f in pdf_files:
        print(f"  - {f}")

    # In production, would:
    # 1. Extract text from each PDF
    # 2. Chunk text into segments
    # 3. Generate embeddings using OpenAI
    # 4. Upload to Qdrant

    print("\nIngestion would process:")
    print("  1. Extract text from PDFs using pdfplumber/PyMuPDF")
    print("  2. Chunk text into overlapping segments")
    print("  3. Generate embeddings with text-embedding-3-large")
    print("  4. Upload vectors to Qdrant with metadata")

    print("\nTo complete ingestion, ensure you have:")
    print("  - OPENAI_API_KEY set in .env")
    print("  - QDRANT_URL and QDRANT_API_KEY set in .env")


if __name__ == "__main__":
    main()
