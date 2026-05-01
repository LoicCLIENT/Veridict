"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, type Caso } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { MapaReconstruccion } from "@/components/MapaReconstruccion";
import { CronologiaTimeline } from "@/components/CronologiaTimeline";
import { CalculosFisicos } from "@/components/CalculosFisicos";
import { RazonamientoLegal } from "@/components/RazonamientoLegal";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Map,
  Clock,
  Calculator,
  Scale,
  Download,
  Play,
  RefreshCw,
} from "lucide-react";

export default function CasoDetailPage() {
  const params = useParams();
  const casoId = params.id as string;
  const [caso, setCaso] = useState<Caso | null>(null);
  const [loading, setLoading] = useState(true);
  const { panelActivo, setPanelActivo, procesando, progreso, etapaActual } =
    useAppStore();

  useEffect(() => {
    async function loadCaso() {
      try {
        const data = await api.getCaso(casoId);
        setCaso(data);
      } catch (error) {
        console.error("Error loading caso:", error);
        // Mock data para desarrollo
        setCaso({
          id: casoId,
          estado: "completado",
          fecha_accidente: "2026-04-15T14:30:00Z",
          ubicacion: { lat: 40.4168, lon: -3.7038 },
          tipo_colision: "lateral",
          vehiculos: [],
          documentos: [],
          fotos: [],
          resultado: {
            cronologia: [
              { timestamp: 0, descripcion: "Vehiculo A circula por carril derecho a 67 km/h" },
              { timestamp: 2, descripcion: "Vehiculo B inicia cambio de carril sin senalizar" },
              { timestamp: 3, descripcion: "Vehiculo A detecta peligro e inicia frenada" },
              { timestamp: 4, descripcion: "Colision lateral en zona delantera derecha" },
            ],
            calculos: [
              {
                nombre: "Velocidad pre-frenada (Stannard Baker)",
                formula: "V = sqrt(2 * mu * g * d)",
                valor: 67.3,
                unidad: "km/h",
                justificacion: "Huella de frenada de 12.5m, mu=0.65 (asfalto mojado)",
              },
              {
                nombre: "EBS por deformacion (CRASH3)",
                formula: "EBS = sqrt((A*C + B*C^2/2) / m)",
                valor: 45.2,
                unidad: "km/h",
                justificacion: "Deformacion media 23cm, coeficientes NHTSA para modelo",
              },
            ],
            infracciones: [
              {
                articulo: "Art. 74.1 RGC",
                descripcion: "Circular a velocidad superior a la permitida",
                vehiculo: "A",
                fuente: "BOE-A-2003-23514",
              },
              {
                articulo: "Art. 72.1 RGC",
                descripcion: "Cambio de carril sin senalizar la maniobra",
                vehiculo: "B",
                fuente: "BOE-A-2003-23514",
              },
            ],
            veredicto: { culpa_a: 0.65, culpa_b: 0.35, confidence: 0.89 },
            compatibilidad_versiones: {
              a: true,
              b: false,
              justificacion: "Version de B incompatible con huellas de frenada observadas",
            },
            devils_advocate_passed: true,
            pdf_url: "/api/casos/1/pdf",
            sigstore_hash: "sha256:abc123...",
          },
        });
      } finally {
        setLoading(false);
      }
    }
    loadCaso();
  }, [casoId]);

  const handleAnalizar = async () => {
    if (!caso) return;
    try {
      await api.analizarCaso(caso.id);
    } catch (error) {
      console.error("Error starting analysis:", error);
    }
  };

  const handleDownloadPdf = async () => {
    if (!caso) return;
    try {
      const blob = await api.downloadPdf(caso.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `dictamen_${caso.id}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading PDF:", error);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        Cargando caso...
      </div>
    );
  }

  if (!caso) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        Caso no encontrado
      </div>
    );
  }

  const tabs = [
    { id: "mapa", label: "Mapa", icon: Map },
    { id: "cronologia", label: "Cronologia", icon: Clock },
    { id: "calculos", label: "Calculos", icon: Calculator },
    { id: "legal", label: "Legal", icon: Scale },
  ] as const;

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Caso #{caso.id}</h1>
          <p className="text-muted-foreground">
            {new Date(caso.fecha_accidente).toLocaleDateString("es-ES", {
              dateStyle: "full",
            })}
          </p>
        </div>
        <div className="flex gap-2">
          {caso.estado === "creado" && (
            <Button onClick={handleAnalizar}>
              <Play className="w-4 h-4 mr-2" />
              Analizar
            </Button>
          )}
          {caso.estado === "completado" && (
            <Button onClick={handleDownloadPdf}>
              <Download className="w-4 h-4 mr-2" />
              Descargar PDF
            </Button>
          )}
        </div>
      </div>

      {/* Progress bar durante procesamiento */}
      {procesando && (
        <Card className="p-4 mb-6">
          <div className="flex items-center gap-4 mb-2">
            <RefreshCw className="w-4 h-4 animate-spin" />
            <span className="font-medium">{etapaActual}</span>
          </div>
          <Progress value={progreso} />
        </Card>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            variant={panelActivo === tab.id ? "default" : "outline"}
            onClick={() => setPanelActivo(tab.id)}
            className="flex items-center gap-2"
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </Button>
        ))}
      </div>

      {/* Content */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Panel principal */}
        <Card className="min-h-[500px]">
          {panelActivo === "mapa" && (
            <MapaReconstruccion ubicacion={caso.ubicacion} />
          )}
          {panelActivo === "cronologia" && (
            <CronologiaTimeline eventos={caso.resultado?.cronologia || []} />
          )}
          {panelActivo === "calculos" && (
            <CalculosFisicos calculos={caso.resultado?.calculos || []} />
          )}
          {panelActivo === "legal" && (
            <RazonamientoLegal
              infracciones={caso.resultado?.infracciones || []}
              veredicto={caso.resultado?.veredicto}
            />
          )}
        </Card>

        {/* Panel secundario - Resumen */}
        <Card className="p-6">
          <h3 className="font-semibold mb-4">Resumen del Dictamen</h3>

          {caso.resultado ? (
            <div className="space-y-6">
              {/* Veredicto */}
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">
                  Atribucion de culpa
                </h4>
                <div className="flex gap-4">
                  <div className="flex-1 p-4 rounded-lg bg-blue-500/10">
                    <div className="text-xs text-blue-400">Vehiculo A</div>
                    <div className="text-2xl font-bold text-blue-400">
                      {Math.round(caso.resultado.veredicto.culpa_a * 100)}%
                    </div>
                  </div>
                  <div className="flex-1 p-4 rounded-lg bg-orange-500/10">
                    <div className="text-xs text-orange-400">Vehiculo B</div>
                    <div className="text-2xl font-bold text-orange-400">
                      {Math.round(caso.resultado.veredicto.culpa_b * 100)}%
                    </div>
                  </div>
                </div>
              </div>

              {/* Compatibilidad versiones */}
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">
                  Compatibilidad de versiones
                </h4>
                <div className="p-4 rounded-lg bg-secondary">
                  <div className="flex gap-4 mb-2">
                    <span
                      className={`text-sm ${
                        caso.resultado.compatibilidad_versiones.a
                          ? "text-green-400"
                          : "text-red-400"
                      }`}
                    >
                      A: {caso.resultado.compatibilidad_versiones.a ? "Compatible" : "Incompatible"}
                    </span>
                    <span
                      className={`text-sm ${
                        caso.resultado.compatibilidad_versiones.b
                          ? "text-green-400"
                          : "text-red-400"
                      }`}
                    >
                      B: {caso.resultado.compatibilidad_versiones.b ? "Compatible" : "Incompatible"}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {caso.resultado.compatibilidad_versiones.justificacion}
                  </p>
                </div>
              </div>

              {/* Devil's Advocate */}
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">
                  Verificacion adversarial
                </h4>
                <div
                  className={`p-4 rounded-lg ${
                    caso.resultado.devils_advocate_passed
                      ? "bg-green-500/10 text-green-400"
                      : "bg-red-500/10 text-red-400"
                  }`}
                >
                  {caso.resultado.devils_advocate_passed
                    ? "Todas las verificaciones pasadas"
                    : "Requiere revision humana"}
                </div>
              </div>

              {/* Audit */}
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">
                  Audit trail
                </h4>
                <code className="text-xs text-muted-foreground break-all">
                  {caso.resultado.sigstore_hash}
                </code>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">
              Ejecuta el analisis para ver el dictamen
            </p>
          )}
        </Card>
      </div>
    </div>
  );
}
