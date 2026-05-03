"use client";

import type { Documento, Foto } from "@/lib/api";
import { FileText, Image as ImageIcon, ExternalLink } from "lucide-react";

interface Props {
  documentos: Documento[];
  fotos: Foto[];
}

export function DocumentosPanel({ documentos, fotos }: Props) {
  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      {/* Documentos */}
      <section>
        <div className="flex items-center gap-2 mb-3 text-veridict-lime">
          <FileText className="w-4 h-4" />
          <h4 className="text-sm font-medium">
            Documents ({documentos?.length ?? 0})
          </h4>
        </div>
        {!documentos || documentos.length === 0 ? (
          <p className="text-sm text-veridict-gray">No documents.</p>
        ) : (
          <div className="space-y-3">
            {documentos.map((d) => (
              <div
                key={d.id}
                className="p-3 rounded-lg bg-veridict-green-800 border border-veridict-green-600"
              >
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <span className="text-xs px-2 py-0.5 rounded bg-veridict-lime/20 text-veridict-lime uppercase">
                    {d.tipo}
                  </span>
                  {d.numero_atestado && (
                    <span className="text-xs font-mono text-veridict-gray">
                      Nº {d.numero_atestado}
                    </span>
                  )}
                  {d.url && (
                    <a
                      href={d.url}
                      target="_blank"
                      rel="noreferrer"
                      className="ml-auto inline-flex items-center gap-1 text-xs text-veridict-lime hover:underline"
                    >
                      Open <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
                {d.texto_extraido && (
                  <details className="text-sm text-veridict-white">
                    <summary className="cursor-pointer text-xs text-veridict-gray mb-1">
                      Extracted text ({d.texto_extraido.length} chars.)
                    </summary>
                    <pre className="whitespace-pre-wrap text-xs bg-veridict-green-700 p-2 rounded mt-2 max-h-64 overflow-auto">
                      {d.texto_extraido}
                    </pre>
                  </details>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Fotos */}
      <section>
        <div className="flex items-center gap-2 mb-3 text-veridict-lime">
          <ImageIcon className="w-4 h-4" />
          <h4 className="text-sm font-medium">Photos ({fotos?.length ?? 0})</h4>
        </div>
        {!fotos || fotos.length === 0 ? (
          <p className="text-sm text-veridict-gray">No photos.</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {fotos.map((f) => (
              <div
                key={f.id}
                className="rounded-lg bg-veridict-green-800 border border-veridict-green-600 overflow-hidden"
              >
                {f.url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={f.url}
                    alt={f.descripcion ?? "Foto"}
                    className="w-full h-40 object-cover"
                  />
                ) : (
                  <div className="w-full h-40 flex items-center justify-center text-veridict-gray">
                    <ImageIcon className="w-8 h-8" />
                  </div>
                )}
                <div className="p-2 text-xs">
                  {f.descripcion && (
                    <p className="text-veridict-white">{f.descripcion}</p>
                  )}
                  {f.analisis && (
                    <p className="text-veridict-gray italic mt-1">{f.analisis}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
