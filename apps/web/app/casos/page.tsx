"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type Caso } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { FileText, Clock, CheckCircle, AlertTriangle, RefreshCw, Plus } from "lucide-react";

export default function CasosPage() {
  const [casos, setCasos] = useState<Caso[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  const loadCasos = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getCasos();
      setCasos(data);
    } catch (e) {
      console.error("Error loading casos:", e);
      const msg = "No se pudo conectar con el backend.";
      setError(msg);
      toast.error("Error de red", msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCasos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Casos</h1>
        <Link href="/casos/nuevo">
          <Button className="gap-2">
            <Plus className="w-4 h-4" />
            Nuevo caso
          </Button>
        </Link>
      </div>

      {loading ? (
        <div className="text-center py-12 text-muted-foreground">
          Cargando casos...
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <AlertTriangle className="w-10 h-10 text-yellow-500 mx-auto mb-3" />
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button onClick={loadCasos} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Reintentar
          </Button>
        </div>
      ) : casos.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
          <p className="text-muted-foreground mb-4">No hay casos todavía</p>
          <Link href="/casos/nuevo">
            <Button className="gap-2">
              <Plus className="w-4 h-4" />
              Crear primer caso
            </Button>
          </Link>
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
