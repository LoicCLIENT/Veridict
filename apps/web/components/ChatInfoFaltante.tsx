"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { InformePericial, InfoFaltante } from "@veridict/types";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MessageCircle, Send, Loader2, AlertCircle, CheckCircle2, Sparkles, Camera, Pencil } from "lucide-react";

type StepStatus = "pending" | "running" | "done" | "error";
interface ProcesoStep {
  id: string;        // "annot" | "C1" | "C2" ...
  label: string;
  status: StepStatus;
}

interface Props {
  casoId: string;
  informe: InformePericial;
  onUpdate: (nuevo: InformePericial) => void;
  onAffectedRespuestas?: (ids: string[]) => void;
}

export function ChatInfoFaltante({
  casoId,
  informe,
  onUpdate,
  onAffectedRespuestas,
}: Props) {
  const [activeId, setActiveId] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [proceso, setProceso] = useState<ProcesoStep[] | null>(null);
  const [procesoErr, setProcesoErr] = useState<string | null>(null);

  const pendientes = informe.info_faltante.filter((q) => !q.respondida);
  const respondidas = informe.info_faltante.filter((q) => q.respondida);

  const updateStep = (id: string, patch: Partial<ProcesoStep>) =>
    setProceso((prev) =>
      prev ? prev.map((s) => (s.id === id ? { ...s, ...patch } : s)) : prev
    );

  const enviar = async () => {
    if (!activeId || !draft.trim()) return;
    setSending(true);
    setProcesoErr(null);
    // Paso 1 visible inmediatamente
    setProceso([
      { id: "annot", label: "Anotando tu respuesta en el chat", status: "running" },
    ]);
    try {
      const { informe: tras_start, afecta_a } = await api.iniciarRespuestaIncremental(
        casoId,
        activeId,
        draft.trim()
      );
      onUpdate(tras_start);
      updateStep("annot", { status: "done" });

      if (afecta_a.length === 0) {
        // Sin scope: solo se registró el chat
        setTimeout(() => setProceso(null), 1200);
        setDraft("");
        setActiveId(null);
        return;
      }

      // Crear pasos por cada C_i afectada
      setProceso((prev) => [
        ...(prev ?? []),
        ...afecta_a.map((cid) => ({
          id: cid,
          label: `Reescribiendo ${cid} con Sonnet 4.6 (manteniendo el resto intacto)`,
          status: "pending" as StepStatus,
        })),
      ]);

      // Iterar secuencialmente para que el usuario vea el progreso
      let lastInforme = tras_start;
      for (const cid of afecta_a) {
        updateStep(cid, { status: "running" });
        try {
          lastInforme = await api.editarPasoIncremental(casoId, activeId, cid);
          onUpdate(lastInforme);
          updateStep(cid, { status: "done" });
        } catch (e) {
          console.error(e);
          updateStep(cid, { status: "error" });
          throw e;
        }
      }

      // Resaltar las afectadas en el documento
      onAffectedRespuestas?.(afecta_a);

      setDraft("");
      setActiveId(null);
      // Dejar el resumen visible un par de segundos
      setTimeout(() => setProceso(null), 2500);
    } catch (e) {
      console.error(e);
      setProcesoErr(
        "No se pudo completar la edición incremental. Inténtalo de nuevo."
      );
    } finally {
      setSending(false);
    }
  };

  return (
    <Card className="bg-zinc-900/50 border-zinc-800">
      <CardHeader>
        <CardTitle className="text-lg text-white flex items-center gap-2">
          <MessageCircle className="w-4 h-4 text-blue-400" />
          Información que falta
        </CardTitle>
        <CardDescription>
          Veridict te pregunta por datos que mejorarían el informe. Responde y lo regenera al instante.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Proceso de edición incremental en vivo */}
        {proceso && (
          <ProcesoEdicion steps={proceso} error={procesoErr} />
        )}

        {/* Mensajes previos del chat */}
        {informe.chat.length > 0 && (
          <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
            {informe.chat.map((m, i) => (
              <div
                key={i}
                className={`p-2.5 rounded-lg text-sm ${
                  m.rol === "claude"
                    ? "bg-blue-500/10 border border-blue-500/20 text-zinc-200"
                    : "bg-zinc-800/60 border border-zinc-700 text-zinc-100 ml-4"
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  {m.rol === "claude" ? (
                    <Sparkles className="w-3 h-3 text-blue-400" />
                  ) : (
                    <span className="text-xs font-medium text-zinc-400">Tú</span>
                  )}
                  <span className="text-xs text-zinc-500">
                    {m.rol === "claude" ? "Veridict" : "Perito"}
                  </span>
                </div>
                <p className="text-xs leading-relaxed">{m.contenido}</p>
              </div>
            ))}
          </div>
        )}

        {/* Pendientes */}
        {pendientes.length === 0 && respondidas.length === 0 && (
          <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20 flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
            <div className="text-xs text-green-200/80">
              Veridict no necesita más información para este informe. Si quieres añadir algo, regenera el informe tras editar el caso.
            </div>
          </div>
        )}

        {pendientes.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-wide text-zinc-500">
              Preguntas pendientes ({pendientes.length})
            </p>
            {pendientes.map((q) => (
              <PreguntaItem
                key={q.id}
                pregunta={q}
                isActive={activeId === q.id}
                draft={activeId === q.id ? draft : ""}
                onActivate={() => {
                  setActiveId(q.id);
                  setDraft("");
                }}
                onChange={setDraft}
                onSend={enviar}
                sending={sending}
                casoId={casoId}
                onPhotoUploaded={async () => {
                  // Tras subir foto, regeneramos el informe automáticamente
                  try {
                    const nuevo = await api.generarInforme(casoId);
                    onUpdate(nuevo);
                  } catch (e) {
                    console.error(e);
                  }
                }}
              />
            ))}
          </div>
        )}

        {/* Respondidas */}
        {respondidas.length > 0 && (
          <div className="space-y-1.5 pt-2 border-t border-zinc-800">
            <p className="text-xs uppercase tracking-wide text-zinc-500">
              Ya respondidas ({respondidas.length})
            </p>
            {respondidas.map((q) => (
              <div key={q.id} className="text-xs text-zinc-500 flex items-start gap-2">
                <CheckCircle2 className="w-3 h-3 text-green-400 flex-shrink-0 mt-0.5" />
                <span className="line-through">{q.pregunta}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function FotoUploadInline({
  casoId,
  contexto,
  onUploaded,
}: {
  casoId: string;
  contexto: string;
  onUploaded: () => void;
}) {
  const [uploading, setUploading] = useState(false);
  const [info, setInfo] = useState<string | null>(null);

  const handle = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setInfo(null);
    try {
      const result = await api.uploadFoto(casoId, file);
      setInfo(
        result?.descripcion
          ? `✓ Indexada: ${result.descripcion}`
          : "✓ Foto subida e indexada."
      );
      onUploaded();
    } catch (err) {
      console.error(err);
      setInfo("Error al subir la foto.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <label
      className={`mt-2 mb-2 flex items-center gap-2 px-2 py-1.5 rounded border border-dashed cursor-pointer text-xs transition-colors ${
        uploading
          ? "border-blue-500 bg-blue-500/10 text-blue-300"
          : "border-amber-500/40 bg-amber-500/5 text-amber-200 hover:bg-amber-500/10"
      }`}
      title={contexto}
    >
      {uploading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Camera className="w-3.5 h-3.5" />}
      <span>{uploading ? "Indexando…" : info ?? "Subir la foto que pide Veridict"}</span>
      <input
        type="file"
        accept="image/*"
        onChange={handle}
        disabled={uploading}
        className="hidden"
      />
    </label>
  );
}

function PreguntaItem({
  pregunta,
  isActive,
  draft,
  onActivate,
  onChange,
  onSend,
  sending,
  casoId,
  onPhotoUploaded,
}: {
  pregunta: InfoFaltante;
  isActive: boolean;
  draft: string;
  onActivate: () => void;
  onChange: (s: string) => void;
  onSend: () => void;
  sending: boolean;
  casoId: string;
  onPhotoUploaded: () => void;
}) {
  const colorByPriority =
    pregunta.prioridad === "bloqueante"
      ? "border-red-500/40 bg-red-500/5"
      : pregunta.prioridad === "recomendable"
      ? "border-amber-500/30 bg-amber-500/5"
      : "border-zinc-700 bg-zinc-900/40";

  const labelByPriority =
    pregunta.prioridad === "bloqueante"
      ? "Bloqueante"
      : pregunta.prioridad === "recomendable"
      ? "Recomendable"
      : "Mejora";

  return (
    <div className={`p-3 rounded-lg border ${colorByPriority}`}>
      <div className="flex items-start gap-2 mb-2">
        <AlertCircle className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] uppercase tracking-wide text-zinc-500">
              {labelByPriority}
            </span>
            {pregunta.afecta_a.length > 0 && (
              <span className="text-[10px] text-zinc-500">→ afecta {pregunta.afecta_a.join(", ")}</span>
            )}
          </div>
          <p className="text-sm text-white leading-snug">{pregunta.pregunta}</p>
          <p className="text-xs text-zinc-500 mt-1 italic">{pregunta.motivo}</p>
        </div>
      </div>

      {pregunta.requiere_foto && (
        <FotoUploadInline
          casoId={casoId}
          contexto={pregunta.pregunta}
          onUploaded={onPhotoUploaded}
        />
      )}

      {!isActive ? (
        <button
          type="button"
          onClick={onActivate}
          className="text-xs text-blue-400 hover:text-blue-300"
        >
          Responder por texto →
        </button>
      ) : (
        <div className="space-y-2">
          <textarea
            rows={3}
            value={draft}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Escribe la información que tienes…"
            className="w-full px-2 py-1.5 text-sm rounded border border-zinc-700 bg-zinc-900 text-white placeholder:text-zinc-500 focus:border-blue-500 outline-none resize-none"
            autoFocus
          />
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              size="sm"
              onClick={onSend}
              disabled={sending || !draft.trim()}
              className="bg-blue-600 hover:bg-blue-500 text-xs h-7"
            >
              {sending ? (
                <>
                  <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                  Procesando…
                </>
              ) : (
                <>
                  <Send className="w-3 h-3 mr-1" />
                  Enviar
                </>
              )}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function ProcesoEdicion({
  steps,
  error,
}: {
  steps: ProcesoStep[];
  error: string | null;
}) {
  const total = steps.length;
  const done = steps.filter((s) => s.status === "done").length;
  const running = steps.find((s) => s.status === "running");
  const allDone = done === total && !error;

  return (
    <div
      className={`rounded-lg border p-3 space-y-2 ${
        error
          ? "border-red-500/40 bg-red-500/5"
          : allDone
          ? "border-emerald-500/30 bg-emerald-500/5"
          : "border-blue-500/30 bg-blue-500/5"
      }`}
    >
      <div className="flex items-center gap-2">
        {error ? (
          <AlertCircle className="w-3.5 h-3.5 text-red-400" />
        ) : allDone ? (
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
        ) : (
          <Pencil className="w-3.5 h-3.5 text-blue-300" />
        )}
        <span className="text-xs font-semibold text-zinc-100">
          {error
            ? "Error en la edición incremental"
            : allDone
            ? "Edición incremental completada"
            : running
            ? running.label
            : "Iniciando edición incremental"}
        </span>
        <span className="ml-auto text-[10px] uppercase tracking-wide text-zinc-500">
          {done}/{total}
        </span>
      </div>

      <ul className="space-y-1">
        {steps.map((s) => (
          <li
            key={s.id}
            className="flex items-center gap-2 text-xs"
          >
            {s.status === "done" ? (
              <CheckCircle2 className="w-3 h-3 text-emerald-400 flex-shrink-0" />
            ) : s.status === "running" ? (
              <Loader2 className="w-3 h-3 text-blue-300 animate-spin flex-shrink-0" />
            ) : s.status === "error" ? (
              <AlertCircle className="w-3 h-3 text-red-400 flex-shrink-0" />
            ) : (
              <span className="w-3 h-3 rounded-full border border-zinc-600 flex-shrink-0" />
            )}
            <span
              className={
                s.status === "done"
                  ? "text-zinc-400 line-through"
                  : s.status === "running"
                  ? "text-blue-100"
                  : s.status === "error"
                  ? "text-red-200"
                  : "text-zinc-500"
              }
            >
              {s.label}
            </span>
          </li>
        ))}
      </ul>

      {error && (
        <p className="text-[11px] text-red-300">{error}</p>
      )}
      {allDone && (
        <p className="text-[11px] text-emerald-200/80">
          Solo se han reescrito las conclusiones afectadas — el resto del informe
          (resumen, fichas, cálculos, normativa…) queda intacto.
        </p>
      )}
    </div>
  );
}
