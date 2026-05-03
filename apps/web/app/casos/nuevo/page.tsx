"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";
import {
  FileText,
  Camera,
  MapPin,
  Car,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Plus,
  Trash2,
  ClipboardList,
  HeartPulse,
  Paperclip,
  Wand2,
  Upload,
} from "lucide-react";

type TipoEncargoUI =
  | "responsabilidad_trafico"
  | "velocidad_impacto"
  | "seguridad_pasiva"
  | "mecanica_fallo"
  | "atropello"
  | "cuantia_danos"
  | "otro";

type ParteUI = "demandante" | "demandado" | "imparcial" | "aseguradora";

type FuenteVelocidad = "declaracion_conductor" | "tacografo" | "edr" | "testigo" | "otro";

interface VehiculoForm {
  id: string;
  matricula: string;
  marca: string;
  modelo: string;
  anio: string;
  color: string;
  conductor: string;
}

interface VelocidadForm {
  vehiculo_id: string;
  valor_kmh: string;
  fuente: FuenteVelocidad;
}

interface LesionForm {
  ocupante: string;
  vehiculo_id: string;
  zona_corporal: string;
  gravedad: "leve" | "moderada" | "grave" | "muy_grave" | "fallecimiento";
  dias_baja: string;
}

const ENCARGO_PRESETS: Record<TipoEncargoUI, { label: string; preguntasSugeridas: string[] }> = {
  responsabilidad_trafico: {
    label: "Responsabilidad en accidente de tráfico",
    preguntasSugeridas: [
      "¿Qué vehículo cometió la infracción que originó el siniestro?",
      "¿Qué artículos del RGC/LSV resultan aplicables?",
    ],
  },
  velocidad_impacto: {
    label: "Determinación de velocidad de impacto",
    preguntasSugeridas: [
      "¿A qué velocidad circulaba cada vehículo al momento de la colisión?",
      "¿Es compatible la velocidad declarada con la dinámica observada?",
    ],
  },
  seguridad_pasiva: {
    label: "Sistemas de seguridad pasiva (airbag, cinturón…)",
    preguntasSugeridas: [
      "¿Debió activarse el airbag?",
      "¿Hubieran sido distintas las lesiones si hubiese funcionado correctamente?",
    ],
  },
  mecanica_fallo: {
    label: "Fallo mecánico",
    preguntasSugeridas: ["¿Existe evidencia de un fallo mecánico previo al siniestro?"],
  },
  atropello: {
    label: "Atropello",
    preguntasSugeridas: [
      "¿A qué velocidad se produjo el atropello?",
      "¿Era evitable la colisión en condiciones de conducción diligente?",
    ],
  },
  cuantia_danos: {
    label: "Cuantía y proporcionalidad de daños",
    preguntasSugeridas: ["¿Es proporcional el presupuesto de reparación a los daños observados?"],
  },
  otro: {
    label: "Otro",
    preguntasSugeridas: [],
  },
};

export default function NuevoCasoPage() {
  const router = useRouter();
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{ current: number; total: number; current_name?: string } | null>(null);
  const [showAdjuntos, setShowAdjuntos] = useState(false);

  // ── Bloque 0: Encargo pericial
  const [encargo, setEncargo] = useState({
    tipo: "responsabilidad_trafico" as TipoEncargoUI,
    preguntas: [""] as string[],
    solicitante: "",
    parte: "imparcial" as ParteUI,
    procedimiento: "",
    observaciones: "",
  });

  // ── Bloque 1: Datos del siniestro
  const [siniestro, setSiniestro] = useState({
    fecha_accidente: "",
    hora_accidente: "",
    tipo_colision: "alcance",
    direccion: "",
    lat: "",
    lon: "",
  });

  // ── Bloque 2: Vehículos (lo MÍNIMO que aporta el perito)
  const [vehiculos, setVehiculos] = useState<VehiculoForm[]>([
    { id: "A", matricula: "", marca: "", modelo: "", anio: "", color: "", conductor: "" },
    { id: "B", matricula: "", marca: "", modelo: "", anio: "", color: "", conductor: "" },
  ]);

  // ── Bloque 3: Hechos del atestado
  const [atestado, setAtestado] = useState({
    numero_atestado: "",
    cuerpo_actuante: "guardia_civil" as string,
    hay_huellas_frenada: "no_consta" as "si" | "no" | "no_consta",
    condiciones_meteorologicas: "",
    estado_calzada: "",
    visibilidad: "",
    declaraciones: "",
  });
  const [velocidades, setVelocidades] = useState<VelocidadForm[]>([]);

  // ── Bloque 4: Lesiones
  const [lesiones, setLesiones] = useState<LesionForm[]>([]);

  // ── Bloque 5: Adjuntos (anexo, NO input para extracción)
  const [files, setFiles] = useState<{
    atestado?: File;
    fotos: File[];
    informeMedico?: File;
    presupuesto?: File;
    otros: File[];
  }>({ fotos: [], otros: [] });

  // ── Persistencia automática del formulario en localStorage ────────────────
  // Las fotos (objetos File) NO pueden persistirse en localStorage; el resto sí.
  const STORAGE_KEY = "veridict_nuevo_caso_draft_v1";
  const restoredRef = useRef(false);
  const [draftRestaurado, setDraftRestaurado] = useState(false);

  // 1) Cargar al montar (una sola vez)
  useEffect(() => {
    if (restoredRef.current) return;
    restoredRef.current = true;
    try {
      const raw = typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
      if (!raw) return;
      const draft = JSON.parse(raw);
      if (draft.encargo) setEncargo(draft.encargo);
      if (draft.siniestro) setSiniestro(draft.siniestro);
      if (draft.vehiculos) setVehiculos(draft.vehiculos);
      if (draft.atestado) setAtestado(draft.atestado);
      if (draft.velocidades) setVelocidades(draft.velocidades);
      if (draft.lesiones) setLesiones(draft.lesiones);
      setDraftRestaurado(true);
    } catch (e) {
      console.warn("No se pudo restaurar el borrador:", e);
    }
  }, []);

  // 2) Guardar en cada cambio (debounced suficiente con un setTimeout corto)
  useEffect(() => {
    if (!restoredRef.current) return;
    if (typeof window === "undefined") return;
    const t = setTimeout(() => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
          encargo, siniestro, vehiculos, atestado, velocidades, lesiones,
          savedAt: new Date().toISOString(),
        }));
      } catch (e) {
        // localStorage lleno o desactivado; ignoramos
      }
    }, 250);
    return () => clearTimeout(t);
  }, [encargo, siniestro, vehiculos, atestado, velocidades, lesiones]);

  // ── Importar JSON (rellenar el formulario desde un fichero) ──────────────
  const importarJSON = async (file: File) => {
    try {
      const text = await file.text();
      const data = JSON.parse(text);

      // Encargo
      if (data.encargo) {
        setEncargo({
          tipo: (data.encargo.tipo ?? "responsabilidad_trafico") as TipoEncargoUI,
          preguntas: Array.isArray(data.encargo.preguntas) && data.encargo.preguntas.length > 0
            ? data.encargo.preguntas.map(String)
            : [""],
          solicitante: data.encargo.solicitante ?? "",
          parte: (data.encargo.parte ?? "imparcial") as ParteUI,
          procedimiento: data.encargo.procedimiento ?? "",
          observaciones: data.encargo.observaciones ?? "",
        });
      }

      // Siniestro
      const fecha = data.fecha_accidente ? String(data.fecha_accidente) : "";
      const fechaSolo = fecha.includes("T") ? fecha.split("T")[0] : fecha;
      const horaSolo = fecha.includes("T") ? (fecha.split("T")[1] ?? "").slice(0, 5) : "";
      setSiniestro({
        fecha_accidente: fechaSolo,
        hora_accidente: horaSolo,
        tipo_colision: data.tipo_colision ?? "alcance",
        direccion: data.direccion ?? "",
        lat: data.ubicacion?.lat != null ? String(data.ubicacion.lat) : "",
        lon: data.ubicacion?.lon != null ? String(data.ubicacion.lon) : "",
      });

      // Vehículos
      if (Array.isArray(data.vehiculos_identificacion) && data.vehiculos_identificacion.length > 0) {
        setVehiculos(
          data.vehiculos_identificacion.map((v: any, i: number) => ({
            id: v.id ?? String.fromCharCode(65 + i),
            matricula: v.matricula ?? "",
            marca: v.marca ?? "",
            modelo: v.modelo ?? "",
            anio: v.anio != null ? String(v.anio) : "",
            color: v.color ?? "",
            conductor: v.conductor ?? "",
          })),
        );
      }

      // Atestado + velocidades
      if (data.hechos_atestado) {
        const ha = data.hechos_atestado;
        setAtestado({
          numero_atestado: ha.numero_atestado ?? "",
          cuerpo_actuante: ha.cuerpo_actuante ?? "guardia_civil",
          hay_huellas_frenada:
            ha.hay_huellas_frenada == null
              ? "no_consta"
              : ha.hay_huellas_frenada
                ? "si"
                : "no",
          condiciones_meteorologicas: ha.condiciones_meteorologicas ?? "",
          estado_calzada: ha.estado_calzada ?? "",
          visibilidad: ha.visibilidad ?? "",
          declaraciones: ha.declaraciones ?? "",
        });
        if (Array.isArray(ha.velocidades_declaradas)) {
          setVelocidades(
            ha.velocidades_declaradas.map((v: any) => ({
              vehiculo_id: v.vehiculo_id ?? "A",
              valor_kmh: v.valor_kmh != null ? String(v.valor_kmh) : "",
              fuente: (v.fuente ?? "declaracion_conductor") as FuenteVelocidad,
            })),
          );
        }
      }

      // Lesiones
      if (Array.isArray(data.lesiones)) {
        setLesiones(
          data.lesiones.map((l: any) => ({
            ocupante: l.ocupante ?? "",
            vehiculo_id: l.vehiculo_id ?? "A",
            zona_corporal: l.zona_corporal ?? "",
            gravedad: (l.gravedad ?? "leve") as LesionForm["gravedad"],
            dias_baja: l.dias_baja != null ? String(l.dias_baja) : "",
          })),
        );
      }

      toast.success("JSON importado", "Revisa los campos y pulsa «Generar borrador» cuando quieras.");
    } catch (e) {
      console.error("Error importando JSON:", e);
      toast.error("JSON inválido", "El fichero no se pudo interpretar como un caso.");
    }
  };

  // 3) Limpiar borrador (botón en la UI)
  const limpiarBorrador = () => {
    if (typeof window === "undefined") return;
    if (!confirm("¿Borrar el formulario completo? Esta acción no se puede deshacer.")) return;
    localStorage.removeItem(STORAGE_KEY);
    window.location.reload();
  };

  const addVehiculo = () => {
    const nextId = String.fromCharCode(65 + vehiculos.length);
    setVehiculos([...vehiculos, { id: nextId, matricula: "", marca: "", modelo: "", anio: "", color: "", conductor: "" }]);
  };
  const removeVehiculo = (idx: number) => {
    if (vehiculos.length <= 1) return;
    setVehiculos(vehiculos.filter((_, i) => i !== idx).map((v, i) => ({ ...v, id: String.fromCharCode(65 + i) })));
  };
  const updateVehiculo = (idx: number, patch: Partial<VehiculoForm>) => {
    setVehiculos(vehiculos.map((v, i) => (i === idx ? { ...v, ...patch } : v)));
  };

  const addPregunta = () => setEncargo({ ...encargo, preguntas: [...encargo.preguntas, ""] });
  const updatePregunta = (idx: number, val: string) =>
    setEncargo({ ...encargo, preguntas: encargo.preguntas.map((p, i) => (i === idx ? val : p)) });
  const removePregunta = (idx: number) =>
    setEncargo({ ...encargo, preguntas: encargo.preguntas.filter((_, i) => i !== idx) });
  const cargarPreguntasSugeridas = () => {
    const preset = ENCARGO_PRESETS[encargo.tipo];
    if (preset.preguntasSugeridas.length > 0) {
      setEncargo({ ...encargo, preguntas: [...preset.preguntasSugeridas] });
    }
  };

  const addVelocidad = () =>
    setVelocidades([...velocidades, { vehiculo_id: vehiculos[0]?.id ?? "A", valor_kmh: "", fuente: "declaracion_conductor" }]);
  const updateVelocidad = (idx: number, patch: Partial<VelocidadForm>) =>
    setVelocidades(velocidades.map((v, i) => (i === idx ? { ...v, ...patch } : v)));
  const removeVelocidad = (idx: number) => setVelocidades(velocidades.filter((_, i) => i !== idx));

  const addLesion = () =>
    setLesiones([...lesiones, { ocupante: "", vehiculo_id: vehiculos[0]?.id ?? "A", zona_corporal: "", gravedad: "leve", dias_baja: "" }]);
  const updateLesion = (idx: number, patch: Partial<LesionForm>) =>
    setLesiones(lesiones.map((l, i) => (i === idx ? { ...l, ...patch } : l)));
  const removeLesion = (idx: number) => setLesiones(lesiones.filter((_, i) => i !== idx));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validación mínima
    if (!siniestro.fecha_accidente) {
      toast.error("Falta la fecha", "Indica la fecha del siniestro.");
      return;
    }
    const preguntasValidas = encargo.preguntas.map((p) => p.trim()).filter(Boolean);
    if (preguntasValidas.length === 0) {
      toast.error("Falta el encargo", "Indica al menos una pregunta a responder en el peritaje.");
      return;
    }
    const vehiculosValidos = vehiculos.filter((v) => v.marca.trim() && v.modelo.trim());
    if (vehiculosValidos.length === 0) {
      toast.error("Faltan vehículos", "Identifica al menos un vehículo (marca y modelo).");
      return;
    }

    setLoading(true);
    try {
      const caso = await api.crearCaso({
        fecha_accidente: siniestro.fecha_accidente,
        tipo_colision: siniestro.tipo_colision as "frontal" | "lateral" | "alcance" | "atropello",
        ubicacion: {
          lat: siniestro.lat ? parseFloat(siniestro.lat) : 0,
          lon: siniestro.lon ? parseFloat(siniestro.lon) : 0,
          direccion: siniestro.direccion?.trim() || undefined,
        },
        encargo: {
          tipo: encargo.tipo,
          preguntas: preguntasValidas,
          solicitante: encargo.solicitante || undefined,
          parte: encargo.parte,
          procedimiento: encargo.procedimiento || undefined,
          observaciones: encargo.observaciones || undefined,
        },
        vehiculos_identificacion: vehiculosValidos.map((v) => ({
          id: v.id,
          matricula: v.matricula || undefined,
          marca: v.marca,
          modelo: v.modelo,
          anio: v.anio ? parseInt(v.anio) : undefined,
          color: v.color || undefined,
          conductor: v.conductor || undefined,
        })),
        hechos_atestado: {
          numero_atestado: atestado.numero_atestado || undefined,
          cuerpo_actuante: atestado.cuerpo_actuante || undefined,
          hay_huellas_frenada:
            atestado.hay_huellas_frenada === "no_consta" ? undefined : atestado.hay_huellas_frenada === "si",
          condiciones_meteorologicas: atestado.condiciones_meteorologicas || undefined,
          estado_calzada: atestado.estado_calzada || undefined,
          visibilidad: atestado.visibilidad || undefined,
          declaraciones: atestado.declaraciones || undefined,
          velocidades_declaradas: velocidades
            .filter((v) => v.valor_kmh)
            .map((v) => ({ vehiculo_id: v.vehiculo_id, valor_kmh: parseFloat(v.valor_kmh), fuente: v.fuente })),
        },
        lesiones: lesiones
          .filter((l) => l.ocupante.trim() && l.zona_corporal.trim())
          .map((l) => ({
            ocupante: l.ocupante,
            vehiculo_id: l.vehiculo_id || undefined,
            zona_corporal: l.zona_corporal,
            gravedad: l.gravedad,
            dias_baja: l.dias_baja ? parseInt(l.dias_baja) : undefined,
          })),
      });

      // Adjuntos como evidencia
      if (files.atestado) {
        setUploadProgress({ current: 0, total: files.fotos.length + 1, current_name: "atestado" });
        await api.uploadAtestado(caso.id, files.atestado);
      }
      for (let i = 0; i < files.fotos.length; i++) {
        const foto = files.fotos[i];
        setUploadProgress({
          current: i + 1 + (files.atestado ? 1 : 0),
          total: files.fotos.length + (files.atestado ? 1 : 0),
          current_name: foto.name,
        });
        await api.uploadFoto(caso.id, foto);
      }
      setUploadProgress(null);

      toast.success(
        "Caso creado",
        files.fotos.length > 0
          ? `${files.fotos.length} fotos indexadas. Generando informe…`
          : "Veridict completará ficha técnica, normativa y cálculos. Generando informe…"
      );

      // Borrador entregado con éxito → limpiamos el localStorage para la próxima vez
      try { localStorage.removeItem(STORAGE_KEY); } catch {}

      // Disparar la generación del informe; no bloqueamos la navegación
      api.generarInforme(caso.id).catch((err) => console.error("Informe error:", err));
      router.push(`/casos/${caso.id}`);
    } catch (error) {
      console.error("Error creating caso:", error);
      toast.error("Error al crear el caso", "Por favor, verifica los datos e intenta nuevamente.");
    } finally {
      setLoading(false);
    }
  };

  const inputClass =
    "w-full px-3 py-2 rounded-lg border border-zinc-700 bg-zinc-900 text-white placeholder:text-zinc-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors";
  const selectClass =
    "w-full px-3 py-2 rounded-lg border border-zinc-700 bg-zinc-900 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors";
  const labelClass = "block text-sm font-medium text-zinc-300 mb-1.5";

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8 flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Nuevo peritaje</h1>
          <p className="text-zinc-400 mt-2">
            Indica el encargo y los datos que conoces. Veridict completará ficha técnica del vehículo,
            normativa aplicable, simulación física y bibliografía.
          </p>
        </div>
        <label className="flex items-center gap-2 px-3 py-2 rounded-lg border border-zinc-700 bg-zinc-900 hover:border-blue-500/50 cursor-pointer text-sm text-zinc-300 hover:text-white transition-colors flex-shrink-0">
          <Upload className="w-4 h-4" />
          Importar JSON
          <input
            type="file"
            accept="application/json,.json"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) importarJSON(f);
              e.target.value = "";
            }}
          />
        </label>
      </div>

      {draftRestaurado && (
        <div className="mb-6 p-3 rounded-lg border border-blue-500/30 bg-blue-500/5 flex items-center justify-between gap-3">
          <p className="text-sm text-blue-200">
            ✓ Se ha restaurado el borrador guardado automáticamente. Sigue donde lo dejaste.
            <span className="text-blue-400/80 ml-2 text-xs">
              (las fotos no se guardan; vuelve a seleccionarlas si las necesitas)
            </span>
          </p>
          <button
            type="button"
            onClick={limpiarBorrador}
            className="text-xs px-3 py-1.5 rounded border border-zinc-700 text-zinc-300 hover:bg-zinc-800"
          >
            Empezar de cero
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">

        {/* ── Bloque 0: Encargo ─────────────────────────────────────────── */}
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <ClipboardList className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <CardTitle className="text-lg text-white">Encargo pericial</CardTitle>
                <CardDescription>¿Qué te ha pedido el solicitante? El informe responderá a estas preguntas.</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>Tipo de pericia *</label>
                <select
                  value={encargo.tipo}
                  onChange={(e) => setEncargo({ ...encargo, tipo: e.target.value as TipoEncargoUI })}
                  className={selectClass}
                >
                  {Object.entries(ENCARGO_PRESETS).map(([k, v]) => (
                    <option key={k} value={k}>
                      {v.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className={labelClass}>Parte solicitante</label>
                <select value={encargo.parte} onChange={(e) => setEncargo({ ...encargo, parte: e.target.value as ParteUI })} className={selectClass}>
                  <option value="imparcial">Perito judicial / imparcial</option>
                  <option value="demandante">Demandante</option>
                  <option value="demandado">Demandado</option>
                  <option value="aseguradora">Aseguradora</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>Solicitante</label>
                <input
                  type="text"
                  placeholder="Ej: Juzgado de 1ª Instancia nº1 de Vilagarcía"
                  value={encargo.solicitante}
                  onChange={(e) => setEncargo({ ...encargo, solicitante: e.target.value })}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Procedimiento / referencia</label>
                <input
                  type="text"
                  placeholder="Ej: Procedimiento Ordinario 230/2010"
                  value={encargo.procedimiento}
                  onChange={(e) => setEncargo({ ...encargo, procedimiento: e.target.value })}
                  className={inputClass}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className={labelClass}>Preguntas a responder *</label>
                <button
                  type="button"
                  onClick={cargarPreguntasSugeridas}
                  className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                >
                  <Wand2 className="w-3 h-3" />
                  Cargar preguntas tipo
                </button>
              </div>
              <div className="space-y-2">
                {encargo.preguntas.map((p, i) => (
                  <div key={i} className="flex gap-2">
                    <span className="text-xs text-zinc-500 mt-2.5 w-8 flex-shrink-0">C{i + 1}.</span>
                    <textarea
                      rows={2}
                      placeholder="Ej: ¿Debió activarse el airbag del vehículo Nissan?"
                      value={p}
                      onChange={(e) => updatePregunta(i, e.target.value)}
                      className={`${inputClass} resize-none`}
                    />
                    {encargo.preguntas.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removePregunta(i)}
                        className="p-2 text-zinc-500 hover:text-red-400 self-start mt-1"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addPregunta}
                  className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
                >
                  <Plus className="w-4 h-4" />
                  Añadir pregunta
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* ── Bloque 1: Siniestro ───────────────────────────────────────── */}
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <MapPin className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <CardTitle className="text-lg text-white">Datos del siniestro</CardTitle>
                <CardDescription>Cuándo, dónde y cómo. La meteo, vía y geocoding los completaremos automáticamente.</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className={labelClass}>Fecha *</label>
                <input
                  type="date"
                  value={siniestro.fecha_accidente}
                  onChange={(e) => setSiniestro({ ...siniestro, fecha_accidente: e.target.value })}
                  className={inputClass}
                  required
                />
              </div>
              <div>
                <label className={labelClass}>Hora aproximada</label>
                <input
                  type="time"
                  value={siniestro.hora_accidente}
                  onChange={(e) => setSiniestro({ ...siniestro, hora_accidente: e.target.value })}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Tipo de colisión *</label>
                <select
                  value={siniestro.tipo_colision}
                  onChange={(e) => setSiniestro({ ...siniestro, tipo_colision: e.target.value })}
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
            </div>
            <div>
              <label className={labelClass}>Dirección / punto kilométrico</label>
              <input
                type="text"
                placeholder="Ej: AP-9, p.k. 67,400 sentido Vigo"
                value={siniestro.direccion}
                onChange={(e) => setSiniestro({ ...siniestro, direccion: e.target.value })}
                className={inputClass}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>Latitud (opcional)</label>
                <input
                  type="number"
                  step="any"
                  placeholder="Se geocodifica automáticamente"
                  value={siniestro.lat}
                  onChange={(e) => setSiniestro({ ...siniestro, lat: e.target.value })}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Longitud (opcional)</label>
                <input
                  type="number"
                  step="any"
                  placeholder="Se geocodifica automáticamente"
                  value={siniestro.lon}
                  onChange={(e) => setSiniestro({ ...siniestro, lon: e.target.value })}
                  className={inputClass}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* ── Bloque 2: Vehículos ───────────────────────────────────────── */}
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-500/20 rounded-lg">
                  <Car className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <CardTitle className="text-lg text-white">Vehículos implicados</CardTitle>
                  <CardDescription>
                    Identifica cada vehículo. Veridict cargará automáticamente: masa, dimensiones, rigidez, sistemas de seguridad.
                  </CardDescription>
                </div>
              </div>
              <button
                type="button"
                onClick={addVehiculo}
                className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
              >
                <Plus className="w-4 h-4" />
                Añadir
              </button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {vehiculos.map((v, i) => (
              <div key={i} className="p-4 border border-zinc-800 rounded-lg bg-zinc-900/40">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-white">Vehículo {v.id}</span>
                  {vehiculos.length > 1 && (
                    <button type="button" onClick={() => removeVehiculo(i)} className="text-zinc-500 hover:text-red-400">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div>
                    <label className={labelClass}>Matrícula</label>
                    <input
                      type="text"
                      placeholder="0019 FJD"
                      value={v.matricula}
                      onChange={(e) => updateVehiculo(i, { matricula: e.target.value.toUpperCase() })}
                      className={inputClass}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Marca *</label>
                    <input
                      type="text"
                      placeholder="Nissan"
                      value={v.marca}
                      onChange={(e) => updateVehiculo(i, { marca: e.target.value })}
                      className={inputClass}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Modelo *</label>
                    <input
                      type="text"
                      placeholder="Cabstar"
                      value={v.modelo}
                      onChange={(e) => updateVehiculo(i, { modelo: e.target.value })}
                      className={inputClass}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Año</label>
                    <input
                      type="number"
                      placeholder="2008"
                      value={v.anio}
                      onChange={(e) => updateVehiculo(i, { anio: e.target.value })}
                      className={inputClass}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Color</label>
                    <input
                      type="text"
                      placeholder="Blanco"
                      value={v.color}
                      onChange={(e) => updateVehiculo(i, { color: e.target.value })}
                      className={inputClass}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Conductor</label>
                    <input
                      type="text"
                      placeholder="Iniciales / nombre"
                      value={v.conductor}
                      onChange={(e) => updateVehiculo(i, { conductor: e.target.value })}
                      className={inputClass}
                    />
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* ── Bloque 3: Hechos del atestado ─────────────────────────────── */}
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-amber-500/20 rounded-lg">
                <FileText className="w-5 h-5 text-amber-400" />
              </div>
              <div>
                <CardTitle className="text-lg text-white">Hechos del atestado</CardTitle>
                <CardDescription>
                  Datos que figuran en el atestado o que has constatado en la inspección. No transcribas el atestado entero — solo lo relevante.
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>Nº atestado</label>
                <input
                  type="text"
                  placeholder="Ej: 994/08"
                  value={atestado.numero_atestado}
                  onChange={(e) => setAtestado({ ...atestado, numero_atestado: e.target.value })}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Cuerpo actuante</label>
                <select
                  value={atestado.cuerpo_actuante}
                  onChange={(e) => setAtestado({ ...atestado, cuerpo_actuante: e.target.value })}
                  className={selectClass}
                >
                  <option value="guardia_civil">Guardia Civil de Tráfico</option>
                  <option value="policia_local">Policía Local</option>
                  <option value="policia_nacional">Policía Nacional</option>
                  <option value="mossos">Mossos d&apos;Esquadra</option>
                  <option value="ertzaintza">Ertzaintza</option>
                </select>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className={labelClass}>Velocidades declaradas / registradas</label>
                <button type="button" onClick={addVelocidad} className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1">
                  <Plus className="w-4 h-4" />
                  Añadir
                </button>
              </div>
              {velocidades.length === 0 && (
                <p className="text-xs text-zinc-500 italic">Sin velocidades — Veridict las inferirá si los datos físicos lo permiten.</p>
              )}
              <div className="space-y-2">
                {velocidades.map((v, i) => (
                  <div key={i} className="grid grid-cols-12 gap-2">
                    <select
                      value={v.vehiculo_id}
                      onChange={(e) => updateVelocidad(i, { vehiculo_id: e.target.value })}
                      className={`${selectClass} col-span-2`}
                    >
                      {vehiculos.map((veh) => (
                        <option key={veh.id} value={veh.id}>
                          {veh.id}
                        </option>
                      ))}
                    </select>
                    <input
                      type="number"
                      step="0.1"
                      placeholder="km/h"
                      value={v.valor_kmh}
                      onChange={(e) => updateVelocidad(i, { valor_kmh: e.target.value })}
                      className={`${inputClass} col-span-3`}
                    />
                    <select
                      value={v.fuente}
                      onChange={(e) => updateVelocidad(i, { fuente: e.target.value as FuenteVelocidad })}
                      className={`${selectClass} col-span-6`}
                    >
                      <option value="declaracion_conductor">Declaración del conductor</option>
                      <option value="tacografo">Tacógrafo</option>
                      <option value="edr">EDR / centralita</option>
                      <option value="testigo">Testigo</option>
                      <option value="otro">Otra fuente</option>
                    </select>
                    <button type="button" onClick={() => removeVelocidad(i)} className="col-span-1 text-zinc-500 hover:text-red-400">
                      <Trash2 className="w-4 h-4 mx-auto" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className={labelClass}>Huellas de frenada</label>
              <div className="flex gap-2">
                {[
                  { v: "si", label: "Sí, hay huellas" },
                  { v: "no", label: "No se observan" },
                  { v: "no_consta", label: "No consta" },
                ].map((opt) => (
                  <button
                    type="button"
                    key={opt.v}
                    onClick={() => setAtestado({ ...atestado, hay_huellas_frenada: opt.v as "si" | "no" | "no_consta" })}
                    className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
                      atestado.hay_huellas_frenada === opt.v
                        ? "border-blue-500 bg-blue-500/20 text-blue-300"
                        : "border-zinc-700 text-zinc-400 hover:border-zinc-500"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className={labelClass}>Meteorología</label>
                <input
                  type="text"
                  placeholder="Despejado, lluvia leve…"
                  value={atestado.condiciones_meteorologicas}
                  onChange={(e) => setAtestado({ ...atestado, condiciones_meteorologicas: e.target.value })}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Estado de la calzada</label>
                <input
                  type="text"
                  placeholder="Seca / mojada / hielo"
                  value={atestado.estado_calzada}
                  onChange={(e) => setAtestado({ ...atestado, estado_calzada: e.target.value })}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Visibilidad</label>
                <input
                  type="text"
                  placeholder="Buena / reducida / nocturna"
                  value={atestado.visibilidad}
                  onChange={(e) => setAtestado({ ...atestado, visibilidad: e.target.value })}
                  className={inputClass}
                />
              </div>
            </div>

            <div>
              <label className={labelClass}>Declaraciones relevantes</label>
              <textarea
                rows={3}
                placeholder='Ej: "El conductor del vehículo A manifiesta que circulaba a 100 km/h y no vio el camión hasta el último momento."'
                value={atestado.declaraciones}
                onChange={(e) => setAtestado({ ...atestado, declaraciones: e.target.value })}
                className={`${inputClass} resize-none`}
              />
            </div>
          </CardContent>
        </Card>

        {/* ── Bloque 4: Lesiones ────────────────────────────────────────── */}
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-red-500/20 rounded-lg">
                  <HeartPulse className="w-5 h-5 text-red-400" />
                </div>
                <div>
                  <CardTitle className="text-lg text-white">Lesiones</CardTitle>
                  <CardDescription>Si las hay, indícalas para alimentar el análisis de seguridad pasiva y baremo.</CardDescription>
                </div>
              </div>
              <button type="button" onClick={addLesion} className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1">
                <Plus className="w-4 h-4" />
                Añadir
              </button>
            </div>
          </CardHeader>
          <CardContent>
            {lesiones.length === 0 ? (
              <p className="text-sm text-zinc-500 italic">Sin lesiones registradas.</p>
            ) : (
              <div className="space-y-3">
                {lesiones.map((l, i) => (
                  <div key={i} className="grid grid-cols-12 gap-2">
                    <input
                      type="text"
                      placeholder="Ocupante (iniciales)"
                      value={l.ocupante}
                      onChange={(e) => updateLesion(i, { ocupante: e.target.value })}
                      className={`${inputClass} col-span-3`}
                    />
                    <select
                      value={l.vehiculo_id}
                      onChange={(e) => updateLesion(i, { vehiculo_id: e.target.value })}
                      className={`${selectClass} col-span-1`}
                    >
                      {vehiculos.map((v) => (
                        <option key={v.id} value={v.id}>
                          {v.id}
                        </option>
                      ))}
                    </select>
                    <input
                      type="text"
                      placeholder="Zona (extremidades inferiores…)"
                      value={l.zona_corporal}
                      onChange={(e) => updateLesion(i, { zona_corporal: e.target.value })}
                      className={`${inputClass} col-span-4`}
                    />
                    <select
                      value={l.gravedad}
                      onChange={(e) => updateLesion(i, { gravedad: e.target.value as LesionForm["gravedad"] })}
                      className={`${selectClass} col-span-2`}
                    >
                      <option value="leve">Leve</option>
                      <option value="moderada">Moderada</option>
                      <option value="grave">Grave</option>
                      <option value="muy_grave">Muy grave</option>
                      <option value="fallecimiento">Fallecimiento</option>
                    </select>
                    <input
                      type="number"
                      placeholder="Días baja"
                      value={l.dias_baja}
                      onChange={(e) => updateLesion(i, { dias_baja: e.target.value })}
                      className={`${inputClass} col-span-1`}
                    />
                    <button type="button" onClick={() => removeLesion(i)} className="col-span-1 text-zinc-500 hover:text-red-400">
                      <Trash2 className="w-4 h-4 mx-auto" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* ── Bloque 5: Biblioteca visual del caso ─────────────────────── */}
        <Card className="bg-gradient-to-br from-purple-500/5 to-blue-500/5 border-purple-500/20">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <Camera className="w-5 h-5 text-purple-300" />
              </div>
              <div>
                <CardTitle className="text-lg text-white">Biblioteca visual del caso</CardTitle>
                <CardDescription>
                  Sube todas las fotografías que tengas (coche, bici, daños, escena, atestado, croquis, lesiones).
                  El BibliotecaFotosAgent las clasificará automáticamente con visión Claude y el orquestador podrá pedir cualquiera de ellas durante la redacción del informe.
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Drop zone principal multi-foto */}
            <label className={`block p-6 border-2 border-dashed rounded-xl cursor-pointer transition-colors ${
              files.fotos.length > 0
                ? "border-purple-500/50 bg-purple-500/5"
                : "border-zinc-700 hover:border-purple-500/40 hover:bg-purple-500/5"
            }`}>
              <div className="flex flex-col items-center gap-2 text-center">
                <Camera className={`w-8 h-8 ${files.fotos.length > 0 ? "text-purple-300" : "text-zinc-500"}`} />
                {files.fotos.length === 0 ? (
                  <>
                    <p className="text-sm font-medium text-white">Arrastra aquí las fotografías o haz click</p>
                    <p className="text-xs text-zinc-500">JPEG, PNG · varias a la vez · sin límite práctico</p>
                  </>
                ) : (
                  <>
                    <p className="text-sm font-medium text-purple-300">
                      ✓ {files.fotos.length} {files.fotos.length === 1 ? "foto seleccionada" : "fotos seleccionadas"}
                    </p>
                    <p className="text-xs text-zinc-400">Click para añadir más o reemplazar</p>
                  </>
                )}
              </div>
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={(e) => setFiles({ ...files, fotos: [...files.fotos, ...Array.from(e.target.files || [])] })}
                className="hidden"
              />
            </label>

            {/* Preview de las fotos seleccionadas */}
            {files.fotos.length > 0 && (
              <div className="grid grid-cols-3 md:grid-cols-5 gap-2 pt-2">
                {files.fotos.map((f, i) => {
                  const url = URL.createObjectURL(f);
                  return (
                    <div key={i} className="relative group rounded-lg overflow-hidden border border-zinc-800">
                      <img src={url} alt={f.name} className="w-full h-20 object-cover" />
                      <button
                        type="button"
                        onClick={() => setFiles({ ...files, fotos: files.fotos.filter((_, j) => j !== i) })}
                        className="absolute top-1 right-1 w-5 h-5 rounded-full bg-red-500/80 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        ×
                      </button>
                      <div className="absolute bottom-0 left-0 right-0 px-1 py-0.5 bg-black/60 text-white text-[10px] truncate">
                        {f.name}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Documentos PDF anexos colapsables */}
            <div className="pt-3 border-t border-zinc-800">
              <button
                type="button"
                onClick={() => setShowAdjuntos(!showAdjuntos)}
                className="flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
              >
                {showAdjuntos ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                Documentos PDF anexos (atestado completo, parte amistoso, informe médico, presupuesto…)
              </button>
            </div>
          </CardContent>
          {showAdjuntos && (
            <CardContent className="space-y-3 pt-0">
              <div className="grid grid-cols-2 gap-3">
                <label className="p-3 border border-dashed border-zinc-700 rounded-lg hover:border-zinc-500 cursor-pointer">
                  <div className="flex items-center gap-2 mb-1">
                    <FileText className="w-4 h-4 text-blue-400" />
                    <span className="text-sm text-white">Atestado completo (PDF)</span>
                  </div>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setFiles({ ...files, atestado: e.target.files?.[0] })}
                    className="hidden"
                  />
                  <span className="text-xs text-zinc-500">{files.atestado ? `✓ ${files.atestado.name}` : "Click para adjuntar"}</span>
                </label>
                <label className="p-3 border border-dashed border-zinc-700 rounded-lg hover:border-zinc-500 cursor-pointer hidden">
                  <div className="flex items-center gap-2 mb-1">
                    <Camera className="w-4 h-4 text-purple-400" />
                    <span className="text-sm text-white">Fotografías</span>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={(e) => setFiles({ ...files, fotos: Array.from(e.target.files || []) })}
                    className="hidden"
                  />
                  <span className="text-xs text-zinc-500">{files.fotos.length > 0 ? `✓ ${files.fotos.length} fotos` : "Click para adjuntar"}</span>
                </label>
                <label className="p-3 border border-dashed border-zinc-700 rounded-lg hover:border-zinc-500 cursor-pointer">
                  <div className="flex items-center gap-2 mb-1">
                    <FileText className="w-4 h-4 text-red-400" />
                    <span className="text-sm text-white">Informe médico</span>
                  </div>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setFiles({ ...files, informeMedico: e.target.files?.[0] })}
                    className="hidden"
                  />
                  <span className="text-xs text-zinc-500">{files.informeMedico ? "✓ Adjunto" : "Click para adjuntar"}</span>
                </label>
                <label className="p-3 border border-dashed border-zinc-700 rounded-lg hover:border-zinc-500 cursor-pointer">
                  <div className="flex items-center gap-2 mb-1">
                    <FileText className="w-4 h-4 text-emerald-400" />
                    <span className="text-sm text-white">Presupuestos / facturas</span>
                  </div>
                  <input
                    type="file"
                    accept=".pdf,image/*"
                    onChange={(e) => setFiles({ ...files, presupuesto: e.target.files?.[0] })}
                    className="hidden"
                  />
                  <span className="text-xs text-zinc-500">{files.presupuesto ? "✓ Adjunto" : "Click para adjuntar"}</span>
                </label>
              </div>
            </CardContent>
          )}
        </Card>

        {/* ── Resumen de lo que hará Veridict ───────────────────────────── */}
        <div className="p-4 rounded-xl border border-blue-500/30 bg-gradient-to-br from-blue-500/10 to-purple-500/10">
          <div className="flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-zinc-300 space-y-1">
              <p className="font-medium text-white">Veridict completará automáticamente:</p>
              <ul className="text-xs text-zinc-400 space-y-0.5 list-disc pl-4">
                <li>Ficha técnica de cada vehículo (masa, dimensiones, rigidez, sistemas de seguridad).</li>
                <li>Geocoding, meteorología histórica y características de la vía.</li>
                <li>Simulación física dirigida por el encargo (CRASH3, Stannard Baker, balance de momento, perfil de aceleración…).</li>
                <li>Normativa aplicable (RGC, LSV, ECE, FMVSS, RGV) y jurisprudencia relevante.</li>
                <li>Bibliografía técnica (papers SAE, anales de ingeniería, NHTSA).</li>
                <li>Borrador de informe UNE-EN 16775 que responde a las preguntas del encargo.</li>
              </ul>
            </div>
          </div>
        </div>

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
            disabled={loading}
            className="flex-1 bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50"
          >
            {loading ? (
              uploadProgress ? (
                <>
                  <span className="animate-spin mr-2">📷</span>
                  Indexando foto {uploadProgress.current}/{uploadProgress.total}…
                </>
              ) : (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Procesando…
                </>
              )
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generar borrador del informe
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
