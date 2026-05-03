"use client";

import { useEffect } from "react";
import { useAppStore } from "@/lib/store";
import { CheckCircle2, Loader2, AlertTriangle, Upload } from "lucide-react";

interface Props {
  casoId: string;
}

export function UploadProgressBanner({ casoId }: Props) {
  const upload = useAppStore((s) => s.uploadsPorCaso[casoId]);
  const limpiarUpload = useAppStore((s) => s.limpiarUpload);

  const finalizado = upload ? upload.completed >= upload.total : false;
  const fallidos = upload?.failed.length ?? 0;

  // Auto-limpiar el estado a los 6 s de finalizado para que la barra desaparezca
  useEffect(() => {
    if (!finalizado) return;
    const id = setTimeout(() => limpiarUpload(casoId), 6000);
    return () => clearTimeout(id);
  }, [finalizado, casoId, limpiarUpload]);

  if (!upload || upload.total === 0) return null;

  const pct = Math.round((upload.completed / upload.total) * 100);

  return (
    <div
      className={`mb-6 rounded-xl border px-4 py-3 ${
        finalizado
          ? "border-emerald-500/40 bg-emerald-500/10"
          : "border-blue-500/40 bg-blue-500/10"
      }`}
    >
      <div className="flex items-center gap-3 mb-2">
        {finalizado ? (
          <CheckCircle2 className="w-5 h-5 text-emerald-300 flex-shrink-0" />
        ) : (
          <Loader2 className="w-5 h-5 text-blue-300 animate-spin flex-shrink-0" />
        )}
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-white flex items-center gap-2">
            <Upload className="w-3.5 h-3.5 text-zinc-300" />
            {finalizado ? (
              <>
                Attachments uploaded · <span className="text-emerald-300">{upload.completed}/{upload.total}</span>
                {fallidos > 0 && (
                  <span className="text-yellow-300 inline-flex items-center gap-1 text-xs">
                    <AlertTriangle className="w-3 h-3" />
                    {fallidos} failed
                  </span>
                )}
              </>
            ) : (
              <>
                Uploading attachments in background ·{" "}
                <span className="text-blue-300">
                  {upload.completed}/{upload.total}
                </span>
              </>
            )}
          </div>
        </div>
        <div className="text-sm font-bold text-white tabular-nums">{pct}%</div>
      </div>
      <div className="h-1.5 rounded-full bg-zinc-800 overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${
            finalizado ? "bg-emerald-400" : "bg-blue-400"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      {!finalizado && (
        <div className="text-[11px] text-zinc-400 mt-2">
          Report generation is running in parallel. You can see progress in the Reasoning tab.
        </div>
      )}
    </div>
  );
}
