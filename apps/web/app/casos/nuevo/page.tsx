"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";
import {
  Upload,
  FileText,
  Camera,
  MapPin,
  Car,
  Ruler,
  ChevronDown,
  ChevronUp,
  Info,
  Sparkles,
  CheckCircle2,
  AlertCircle
} from "lucide-react";

export default function NuevoCasoPage() {
  const router = useRouter();
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Datos mínimos obligatorios
  const [formData, setFormData] = useState({
    fecha_accidente: "",
    tipo_colision: "lateral",
    num_vehiculos: "2",
  });

  // Datos opcionales avanzados (si el perito quiere sobreescribir lo extraído)
  const [advanced, setAdvanced] = useState({
    lat: "",
    lon: "",
    coef_friccion: "",
    huella_frenada_a: "",
    huella_frenada_b: "",
    notas_perito: "",
  });

  // Archivos - LO PRINCIPAL
  const [files, setFiles] = useState<{
    atestado?: File;
    parteAmistoso?: File;
    croquis?: File;
    fotos: File[];
    informeMedico?: File;
  }>({ fotos: [] });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!files.atestado && files.fotos.length === 0) {
      toast.error(
        "Documentación requerida",
        "Debe adjuntar al menos el atestado policial o fotografías del accidente."
      );
      return;
    }

    setLoading(true);

    try {
      const caso = await api.crearCaso({
        fecha_accidente: formData.fecha_accidente,
        tipo_colision: formData.tipo_colision as "frontal" | "lateral" | "alcance" | "atropello",
        num_vehiculos: parseInt(formData.num_vehiculos),
        ubicacion: advanced.lat && advanced.lon ? {
          lat: parseFloat(advanced.lat),
          lon: parseFloat(advanced.lon),
        } : undefined,
        datos_perito: showAdvanced ? {
          coef_friccion: advanced.coef_friccion ? parseFloat(advanced.coef_friccion) : undefined,
          huella_frenada_a: advanced.huella_frenada_a ? parseFloat(advanced.huella_frenada_a) : undefined,
          huella_frenada_b: advanced.huella_frenada_b ? parseFloat(advanced.huella_frenada_b) : undefined,
          notas: advanced.notas_perito || undefined,
        } : undefined,
      });

      // Upload archivos
      if (files.atestado) {
        await api.uploadAtestado(caso.id, files.atestado);
      }
      for (const foto of files.fotos) {
        await api.uploadFoto(caso.id, foto);
      }

      toast.success(
        "Caso creado",
        "Los documentos se están procesando con IA. Será redirigido al análisis."
      );

      router.push(`/casos/${caso.id}`);
    } catch (error) {
      console.error("Error creating caso:", error);
      toast.error(
        "Error al crear el caso",
        "Por favor, verifica los datos e intenta nuevamente."
      );
    } finally {
      setLoading(false);
    }
  };

  const inputClass = "w-full px-3 py-2 rounded-lg border border-zinc-700 bg-zinc-900 text-white placeholder:text-zinc-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors";
  const selectClass = "w-full px-3 py-2 rounded-lg border border-zinc-700 bg-zinc-900 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors";
  const labelClass = "block text-sm font-medium text-zinc-300 mb-1.5";

  const totalFiles = (files.atestado ? 1 : 0) + (files.parteAmistoso ? 1 : 0) + (files.croquis ? 1 : 0) + files.fotos.length + (files.informeMedico ? 1 : 0);

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Nuevo Caso</h1>
        <p className="text-zinc-400 mt-2">
          Sube la documentación y nuestra IA extraerá automáticamente todos los datos.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">

        {/* SECCIÓN 1: Documentación (LO PRINCIPAL) */}
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <FileText className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <CardTitle className="text-lg text-white">Documentación del caso</CardTitle>
                <CardDescription>Sube los documentos disponibles - la IA hará el resto</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">

            {/* Atestado - Principal */}
            <div className={`p-4 border-2 border-dashed rounded-xl transition-colors ${
              files.atestado ? 'border-green-500/50 bg-green-500/5' : 'border-zinc-700 hover:border-zinc-500'
            }`}>
              <label className="cursor-pointer block">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-blue-400" />
                    <span className="font-medium text-white">Atestado policial</span>
                    <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded">Recomendado</span>
                  </div>
                  {files.atestado && <CheckCircle2 className="w-5 h-5 text-green-400" />}
                </div>
                <p className="text-xs text-zinc-500 mb-3">
                  Contiene: datos vehículos, conductores, declaraciones, croquis, condiciones...
                </p>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setFiles({ ...files, atestado: e.target.files?.[0] })}
                  className="hidden"
                />
                <div className="text-sm text-zinc-400">
                  {files.atestado ? (
                    <span className="text-green-400">✓ {files.atestado.name}</span>
                  ) : (
                    <span className="text-blue-400 hover:text-blue-300">Click para seleccionar PDF</span>
                  )}
                </div>
              </label>
            </div>

            {/* Grid de otros documentos */}
            <div className="grid grid-cols-2 gap-3">
              {/* Fotos */}
              <div className={`p-3 border border-dashed rounded-lg transition-colors ${
                files.fotos.length > 0 ? 'border-green-500/50 bg-green-500/5' : 'border-zinc-700 hover:border-zinc-500'
              }`}>
                <label className="cursor-pointer block">
                  <div className="flex items-center gap-2 mb-1">
                    <Camera className="w-4 h-4 text-purple-400" />
                    <span className="text-sm font-medium text-white">Fotografías</span>
                  </div>
                  <p className="text-xs text-zinc-500 mb-2">Daños, escena, huellas</p>
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={(e) => setFiles({ ...files, fotos: Array.from(e.target.files || []) })}
                    className="hidden"
                  />
                  <div className="text-xs">
                    {files.fotos.length > 0 ? (
                      <span className="text-green-400">✓ {files.fotos.length} fotos</span>
                    ) : (
                      <span className="text-zinc-500">Seleccionar...</span>
                    )}
                  </div>
                </label>
              </div>

              {/* Parte amistoso */}
              <div className={`p-3 border border-dashed rounded-lg transition-colors ${
                files.parteAmistoso ? 'border-green-500/50 bg-green-500/5' : 'border-zinc-700 hover:border-zinc-500'
              }`}>
                <label className="cursor-pointer block">
                  <div className="flex items-center gap-2 mb-1">
                    <FileText className="w-4 h-4 text-orange-400" />
                    <span className="text-sm font-medium text-white">Parte amistoso</span>
                  </div>
                  <p className="text-xs text-zinc-500 mb-2">DAA si existe</p>
                  <input
                    type="file"
                    accept=".pdf,image/*"
                    onChange={(e) => setFiles({ ...files, parteAmistoso: e.target.files?.[0] })}
                    className="hidden"
                  />
                  <div className="text-xs">
                    {files.parteAmistoso ? (
                      <span className="text-green-400">✓ Adjunto</span>
                    ) : (
                      <span className="text-zinc-500">Opcional</span>
                    )}
                  </div>
                </label>
              </div>

              {/* Croquis */}
              <div className={`p-3 border border-dashed rounded-lg transition-colors ${
                files.croquis ? 'border-green-500/50 bg-green-500/5' : 'border-zinc-700 hover:border-zinc-500'
              }`}>
                <label className="cursor-pointer block">
                  <div className="flex items-center gap-2 mb-1">
                    <MapPin className="w-4 h-4 text-green-400" />
                    <span className="text-sm font-medium text-white">Croquis</span>
                  </div>
                  <p className="text-xs text-zinc-500 mb-2">Si está separado</p>
                  <input
                    type="file"
                    accept=".pdf,image/*"
                    onChange={(e) => setFiles({ ...files, croquis: e.target.files?.[0] })}
                    className="hidden"
                  />
                  <div className="text-xs">
                    {files.croquis ? (
                      <span className="text-green-400">✓ Adjunto</span>
                    ) : (
                      <span className="text-zinc-500">Opcional</span>
                    )}
                  </div>
                </label>
              </div>

              {/* Informe médico */}
              <div className={`p-3 border border-dashed rounded-lg transition-colors ${
                files.informeMedico ? 'border-green-500/50 bg-green-500/5' : 'border-zinc-700 hover:border-zinc-500'
              }`}>
                <label className="cursor-pointer block">
                  <div className="flex items-center gap-2 mb-1">
                    <FileText className="w-4 h-4 text-red-400" />
                    <span className="text-sm font-medium text-white">Informe médico</span>
                  </div>
                  <p className="text-xs text-zinc-500 mb-2">Lesiones</p>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setFiles({ ...files, informeMedico: e.target.files?.[0] })}
                    className="hidden"
                  />
                  <div className="text-xs">
                    {files.informeMedico ? (
                      <span className="text-green-400">✓ Adjunto</span>
                    ) : (
                      <span className="text-zinc-500">Opcional</span>
                    )}
                  </div>
                </label>
              </div>
            </div>

            {totalFiles > 0 && (
              <div className="flex items-center gap-2 text-sm text-zinc-400 pt-2">
                <CheckCircle2 className="w-4 h-4 text-green-400" />
                <span>{totalFiles} documento{totalFiles > 1 ? 's' : ''} listo{totalFiles > 1 ? 's' : ''} para procesar</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* SECCIÓN 2: Datos mínimos */}
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Car className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <CardTitle className="text-lg text-white">Información básica</CardTitle>
                <CardDescription>Solo lo esencial para iniciar el análisis</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className={labelClass}>
                  Fecha del accidente *
                </label>
                <input
                  type="date"
                  value={formData.fecha_accidente}
                  onChange={(e) => setFormData({ ...formData, fecha_accidente: e.target.value })}
                  className={inputClass}
                  required
                />
              </div>
              <div>
                <label className={labelClass}>
                  Tipo de colisión *
                </label>
                <select
                  value={formData.tipo_colision}
                  onChange={(e) => setFormData({ ...formData, tipo_colision: e.target.value })}
                  className={selectClass}
                >
                  <option value="frontal">Frontal</option>
                  <option value="lateral">Lateral</option>
                  <option value="alcance">Alcance</option>
                  <option value="atropello">Atropello</option>
                  <option value="multiple">Múltiple</option>
                  <option value="salida_via">Salida de vía</option>
                  <option value="vuelco">Vuelco</option>
                </select>
              </div>
              <div>
                <label className={labelClass}>
                  Nº vehículos
                </label>
                <select
                  value={formData.num_vehiculos}
                  onChange={(e) => setFormData({ ...formData, num_vehiculos: e.target.value })}
                  className={selectClass}
                >
                  <option value="1">1</option>
                  <option value="2">2</option>
                  <option value="3">3</option>
                  <option value="4">4+</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* SECCIÓN 3: Datos avanzados (colapsable) */}
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardHeader
            className="cursor-pointer select-none"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-zinc-700/50 rounded-lg">
                  <Ruler className="w-5 h-5 text-zinc-400" />
                </div>
                <div>
                  <CardTitle className="text-lg text-white">Datos adicionales del perito</CardTitle>
                  <CardDescription>Opcional: sobreescribe o complementa datos extraídos</CardDescription>
                </div>
              </div>
              {showAdvanced ? <ChevronUp className="w-5 h-5 text-zinc-400" /> : <ChevronDown className="w-5 h-5 text-zinc-400" />}
            </div>
          </CardHeader>
          {showAdvanced && (
            <CardContent className="space-y-4 pt-0">
              <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg mb-4">
                <div className="flex gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                  <p className="text-xs text-amber-200/80">
                    Estos datos solo son necesarios si realizó mediciones propias en la inspección
                    o si desea corregir algún dato extraído automáticamente.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>
                    <MapPin className="w-3 h-3 inline mr-1" />
                    Latitud
                  </label>
                  <input
                    type="number"
                    step="any"
                    placeholder="Se extrae del atestado"
                    value={advanced.lat}
                    onChange={(e) => setAdvanced({ ...advanced, lat: e.target.value })}
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className={labelClass}>
                    <MapPin className="w-3 h-3 inline mr-1" />
                    Longitud
                  </label>
                  <input
                    type="number"
                    step="any"
                    placeholder="Se extrae del atestado"
                    value={advanced.lon}
                    onChange={(e) => setAdvanced({ ...advanced, lon: e.target.value })}
                    className={inputClass}
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className={labelClass}>Coef. fricción (μ)</label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="Ej: 0.7"
                    value={advanced.coef_friccion}
                    onChange={(e) => setAdvanced({ ...advanced, coef_friccion: e.target.value })}
                    className={inputClass}
                  />
                  <p className="text-xs text-zinc-500 mt-1">Si midió en campo</p>
                </div>
                <div>
                  <label className={labelClass}>Huella frenada A (m)</label>
                  <input
                    type="number"
                    step="0.1"
                    placeholder="Ej: 12.5"
                    value={advanced.huella_frenada_a}
                    onChange={(e) => setAdvanced({ ...advanced, huella_frenada_a: e.target.value })}
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className={labelClass}>Huella frenada B (m)</label>
                  <input
                    type="number"
                    step="0.1"
                    placeholder="Ej: 8.3"
                    value={advanced.huella_frenada_b}
                    onChange={(e) => setAdvanced({ ...advanced, huella_frenada_b: e.target.value })}
                    className={inputClass}
                  />
                </div>
              </div>

              <div>
                <label className={labelClass}>Notas adicionales del perito</label>
                <textarea
                  placeholder="Observaciones propias de la inspección, discrepancias con el atestado, mediciones adicionales..."
                  value={advanced.notas_perito}
                  onChange={(e) => setAdvanced({ ...advanced, notas_perito: e.target.value })}
                  rows={3}
                  className={`${inputClass} resize-none`}
                />
              </div>
            </CardContent>
          )}
        </Card>

        {/* Submit */}
        <div className="flex gap-4 pt-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
            className="flex-1 border-zinc-700 text-zinc-300 hover:bg-zinc-800"
          >
            Cancelar
          </Button>
          <Button
            type="submit"
            disabled={loading || (totalFiles === 0)}
            className="flex-1 bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50"
          >
            {loading ? (
              <>
                <span className="animate-spin mr-2">⏳</span>
                Procesando...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Analizar con IA
              </>
            )}
          </Button>
        </div>

        {totalFiles === 0 && (
          <p className="text-center text-sm text-zinc-500">
            Adjunta al menos un documento para continuar
          </p>
        )}
      </form>
    </div>
  );
}
