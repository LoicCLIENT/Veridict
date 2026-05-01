"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type Caso } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, FileText, Clock, CheckCircle, AlertTriangle } from "lucide-react";

export default function CasosPage() {
  const [casos, setCasos] = useState<Caso[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCasos() {
      try {
        const data = await api.getDemoCasos();
        setCasos(data);
      } catch (error) {
        console.error("Error loading casos:", error);
        // Casos mock para desarrollo
        setCasos([
          {
            id: "1",
            estado: "completado",
            fecha_accidente: "2026-04-15T14:30:00Z",
            ubicacion: { lat: 40.4168, lon: -3.7038 },
            tipo_colision: "lateral",
            vehiculos: [],
            documentos: [],
            fotos: [],
          },
          {
            id: "2",
            estado: "completado",
            fecha_accidente: "2026-04-20T09:15:00Z",
            ubicacion: { lat: 40.4825, lon: -3.3645 },
            tipo_colision: "atropello",
            vehiculos: [],
            documentos: [],
            fotos: [],
          },
          {
            id: "3",
            estado: "completado",
            fecha_accidente: "2026-04-22T18:45:00Z",
            ubicacion: { lat: 40.4500, lon: -3.7200 },
            tipo_colision: "alcance",
            vehiculos: [],
            documentos: [],
            fotos: [],
          },
        ]);
      } finally {
        setLoading(false);
      }
    }
    loadCasos();
  }, []);

  const estadoIcon = (estado: Caso["estado"]) => {
    switch (estado) {
      case "creado":
        return <FileText className="w-4 h-4" />;
      case "procesando":
        return <Clock className="w-4 h-4 animate-spin" />;
      case "completado":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "escalado_humano":
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
    }
  };

  const tipoLabel = (tipo: Caso["tipo_colision"]) => {
    const labels = {
      frontal: "Frontal",
      lateral: "Lateral",
      alcance: "Alcance",
      atropello: "Atropello",
    };
    return labels[tipo];
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Casos</h1>
        <Link href="/casos/nuevo">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Nuevo caso
          </Button>
        </Link>
      </div>

      {loading ? (
        <div className="text-center py-12 text-muted-foreground">
          Cargando casos...
        </div>
      ) : casos.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No hay casos disponibles
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {casos.map((caso) => (
            <Link key={caso.id} href={`/casos/${caso.id}`}>
              <Card className="hover:border-primary/50 transition cursor-pointer">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-primary bg-primary/10 px-2 py-1 rounded">
                      {tipoLabel(caso.tipo_colision)}
                    </span>
                    {estadoIcon(caso.estado)}
                  </div>
                  <CardTitle className="text-lg">Caso #{caso.id}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {new Date(caso.fecha_accidente).toLocaleDateString("es-ES", {
                      dateStyle: "long",
                    })}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {caso.ubicacion.lat.toFixed(4)}, {caso.ubicacion.lon.toFixed(4)}
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
