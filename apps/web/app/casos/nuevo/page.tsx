"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload, FileText, Camera, MapPin } from "lucide-react";

export default function NuevoCasoPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    fecha_accidente: "",
    lat: "",
    lon: "",
    tipo_colision: "lateral" as const,
  });
  const [files, setFiles] = useState<{
    atestado?: File;
    parte?: File;
    fotos: File[];
  }>({ fotos: [] });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Crear caso
      const caso = await api.crearCaso({
        fecha_accidente: formData.fecha_accidente,
        ubicacion: {
          lat: parseFloat(formData.lat),
          lon: parseFloat(formData.lon),
        },
        tipo_colision: formData.tipo_colision,
      });

      // Upload archivos
      if (files.atestado) {
        await api.uploadAtestado(caso.id, files.atestado);
      }
      for (const foto of files.fotos) {
        await api.uploadFoto(caso.id, foto);
      }

      // Redirigir al caso
      router.push(`/casos/${caso.id}`);
    } catch (error) {
      console.error("Error creating caso:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <h1 className="text-3xl font-bold mb-8">Nuevo Caso</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Datos basicos */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Datos del accidente</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Fecha y hora del accidente
              </label>
              <input
                type="datetime-local"
                value={formData.fecha_accidente}
                onChange={(e) =>
                  setFormData({ ...formData, fecha_accidente: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg border border-input bg-background"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Latitud
                </label>
                <input
                  type="number"
                  step="any"
                  placeholder="40.4168"
                  value={formData.lat}
                  onChange={(e) =>
                    setFormData({ ...formData, lat: e.target.value })
                  }
                  className="w-full px-3 py-2 rounded-lg border border-input bg-background"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Longitud
                </label>
                <input
                  type="number"
                  step="any"
                  placeholder="-3.7038"
                  value={formData.lon}
                  onChange={(e) =>
                    setFormData({ ...formData, lon: e.target.value })
                  }
                  className="w-full px-3 py-2 rounded-lg border border-input bg-background"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Tipo de colision
              </label>
              <select
                value={formData.tipo_colision}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    tipo_colision: e.target.value as typeof formData.tipo_colision,
                  })
                }
                className="w-full px-3 py-2 rounded-lg border border-input bg-background"
              >
                <option value="frontal">Frontal</option>
                <option value="lateral">Lateral</option>
                <option value="alcance">Alcance</option>
                <option value="atropello">Atropello</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Documentos */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Documentos</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                <FileText className="w-4 h-4 inline mr-2" />
                Atestado policial (PDF)
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) =>
                  setFiles({ ...files, atestado: e.target.files?.[0] })
                }
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                <FileText className="w-4 h-4 inline mr-2" />
                Parte amistoso (PDF, opcional)
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) =>
                  setFiles({ ...files, parte: e.target.files?.[0] })
                }
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                <Camera className="w-4 h-4 inline mr-2" />
                Fotos del accidente
              </label>
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={(e) =>
                  setFiles({
                    ...files,
                    fotos: Array.from(e.target.files || []),
                  })
                }
                className="w-full"
              />
              {files.fotos.length > 0 && (
                <p className="text-sm text-muted-foreground mt-1">
                  {files.fotos.length} fotos seleccionadas
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Submit */}
        <div className="flex gap-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
            className="flex-1"
          >
            Cancelar
          </Button>
          <Button type="submit" disabled={loading} className="flex-1">
            {loading ? "Creando..." : "Crear caso"}
          </Button>
        </div>
      </form>
    </div>
  );
}
