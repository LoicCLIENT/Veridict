"""
Veridict AI - Backend API
Reconstruccion forense automatizada de accidentes de trafico
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from routers import casos, upload, analisis, dictamen, demo, data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Veridict API...")
    yield
    # Shutdown
    print("Shutting down Veridict API...")


app = FastAPI(
    title="Veridict AI API",
    description="Sistema multi-agente para reconstruccion forense de accidentes de trafico",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — incluye localhost para la demo HTML
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(casos.router, prefix="/api/casos", tags=["casos"])
app.include_router(upload.router, prefix="/api/casos", tags=["upload"])
app.include_router(analisis.router, prefix="/api/casos", tags=["analisis"])
app.include_router(dictamen.router, prefix="/api/casos", tags=["dictamen"])
app.include_router(demo.router, prefix="/api/demo", tags=["demo"])
app.include_router(data.router, prefix="/api/data", tags=["data"])


@app.get("/demo", include_in_schema=False)
async def demo_ui():
    return FileResponse(os.path.join(os.path.dirname(__file__), "demo_frontend.html"))


@app.get("/")
async def root():
    return {
        "name": "Veridict AI API",
        "version": "0.1.0",
        "status": "running",
        "demo": "http://localhost:8000/demo",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
