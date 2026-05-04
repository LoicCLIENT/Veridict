"use client";

import { useCallback, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Camera,
  FileText,
  Upload,
  X,
  Sparkles,
  ArrowLeft,
  Loader2,
  CheckCircle,
  Image,
} from "lucide-react";
import { FilesForm } from "../types";

interface Step5Props {
  files: FilesForm;
  onChange: (files: FilesForm) => void;
  onSubmit: () => void;
  onBack: () => void;
  isSubmitting: boolean;
}

export function Step5Evidence({ files, onChange, onSubmit, onBack, isSubmitting }: Step5Props) {
  const [isDragging, setIsDragging] = useState(false);

  const handlePhotoDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      const droppedFiles = Array.from(e.dataTransfer.files).filter((f) =>
        f.type.startsWith("image/")
      );
      onChange({ ...files, fotos: [...files.fotos, ...droppedFiles] });
    },
    [files, onChange]
  );

  const handlePhotoSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selected = Array.from(e.target.files || []);
      onChange({ ...files, fotos: [...files.fotos, ...selected] });
    },
    [files, onChange]
  );

  const removePhoto = (idx: number) => {
    onChange({ ...files, fotos: files.fotos.filter((_, i) => i !== idx) });
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl lg:text-4xl font-bold text-veridict-white mb-4"
        >
          Upload evidence
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-lg text-veridict-gray"
        >
          Photos of vehicles, damage, scene, and documents. Our AI will classify and
          analyze each piece of evidence automatically.
        </motion.p>
      </div>

      {/* Photo upload zone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="max-w-4xl mx-auto"
      >
        <div
          onDrop={handlePhotoDrop}
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          className={`
            relative rounded-3xl border-2 border-dashed transition-all duration-300 overflow-hidden
            ${isDragging
              ? "border-veridict-lime bg-veridict-lime/10 scale-[1.01]"
              : files.fotos.length > 0
                ? "border-veridict-lime/30 bg-veridict-lime/5"
                : "border-veridict-green-700/50 hover:border-veridict-lime/30 hover:bg-veridict-green-800/30"
            }
          `}
        >
          {files.fotos.length === 0 ? (
            /* Empty state */
            <label className="flex flex-col items-center justify-center p-12 cursor-pointer">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 border border-purple-500/30 flex items-center justify-center mb-6">
                <Camera className="w-10 h-10 text-purple-400" />
              </div>
              <p className="text-lg font-semibold text-veridict-white mb-2">
                Drop photos here or click to browse
              </p>
              <p className="text-sm text-veridict-gray mb-4">
                JPEG, PNG, HEIC - No limit on number of files
              </p>
              <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-veridict-green-800/50 border border-veridict-green-700/50">
                <Upload className="w-4 h-4 text-veridict-lime" />
                <span className="text-sm font-medium text-veridict-lime">
                  Select files
                </span>
              </div>
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={handlePhotoSelect}
                className="hidden"
              />
            </label>
          ) : (
            /* Photos grid */
            <div className="p-4">
              {/* Grid of photos */}
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3">
                <AnimatePresence initial={false}>
                  {files.fotos.map((foto, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      className="relative group aspect-square rounded-xl overflow-hidden border border-veridict-green-700/50"
                    >
                      <img
                        src={URL.createObjectURL(foto)}
                        alt={foto.name}
                        className="w-full h-full object-cover"
                      />
                      {/* Overlay on hover */}
                      <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <button
                          type="button"
                          onClick={() => removePhoto(idx)}
                          className="w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center hover:bg-red-600 transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                      {/* File name */}
                      <div className="absolute bottom-0 left-0 right-0 px-2 py-1 bg-black/70 text-[10px] text-veridict-gray truncate">
                        {foto.name}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>

                {/* Add more button */}
                <label className="aspect-square rounded-xl border-2 border-dashed border-veridict-green-700/50 hover:border-veridict-lime/30 hover:bg-veridict-green-800/30 cursor-pointer flex flex-col items-center justify-center transition-all">
                  <Camera className="w-6 h-6 text-veridict-gray mb-1" />
                  <span className="text-xs text-veridict-gray">Add more</span>
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handlePhotoSelect}
                    className="hidden"
                  />
                </label>
              </div>

              {/* Photos count */}
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-veridict-green-700/30">
                <div className="flex items-center gap-2">
                  <Image className="w-4 h-4 text-veridict-lime" />
                  <span className="text-sm font-medium text-veridict-white">
                    {files.fotos.length} photo{files.fotos.length !== 1 ? "s" : ""} ready
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => onChange({ ...files, fotos: [] })}
                  className="text-xs text-veridict-gray hover:text-red-400 transition-colors"
                >
                  Clear all
                </button>
              </div>
            </div>
          )}
        </div>
      </motion.div>

      {/* Atestado document upload */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="max-w-4xl mx-auto"
      >
        <div className="flex items-center gap-2 mb-4">
          <FileText className="w-4 h-4 text-veridict-lime" />
          <p className="text-sm font-medium text-veridict-white">
            Police report (atestado)
          </p>
          <span className="text-xs text-veridict-gray/60">PDF</span>
        </div>

        <label className={`
          block rounded-2xl border-2 border-dashed cursor-pointer transition-all duration-300
          ${files.atestado
            ? "border-veridict-lime/40 bg-veridict-lime/5"
            : "border-veridict-green-700/50 hover:border-veridict-lime/30 hover:bg-veridict-green-800/30"
          }
        `}>
          {files.atestado ? (
            <div className="flex items-center gap-4 p-5">
              <div className="w-14 h-14 rounded-xl bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                <FileText className="w-7 h-7 text-blue-400" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-veridict-white truncate">
                  {files.atestado.name}
                </p>
                <p className="text-xs text-veridict-lime flex items-center gap-1 mt-1">
                  <CheckCircle className="w-3 h-3" />
                  Ready to upload
                </p>
              </div>
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  onChange({ ...files, atestado: undefined });
                }}
                className="p-2 rounded-lg hover:bg-red-500/20 text-veridict-gray hover:text-red-400 transition-colors flex-shrink-0"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center p-10 text-center">
              <div className="w-16 h-16 rounded-2xl bg-blue-500/20 border border-blue-500/30 flex items-center justify-center mb-4">
                <FileText className="w-8 h-8 text-blue-400" />
              </div>
              <p className="text-base font-semibold text-veridict-white mb-1">
                Upload the atestado
              </p>
              <p className="text-xs text-veridict-gray mb-4">
                PDF document from the responding police force
              </p>
              <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-veridict-green-800/50 border border-veridict-green-700/50">
                <Upload className="w-4 h-4 text-veridict-lime" />
                <span className="text-sm font-medium text-veridict-lime">
                  Select PDF
                </span>
              </div>
            </div>
          )}
          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={(e) => onChange({ ...files, atestado: e.target.files?.[0] })}
            className="hidden"
          />
        </label>
      </motion.div>

      {/* AI capabilities summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="max-w-3xl mx-auto"
      >
        <div className="p-5 rounded-2xl bg-gradient-to-br from-purple-500/10 via-blue-500/10 to-veridict-lime/5 border border-purple-500/20">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/30 to-blue-500/30 flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-6 h-6 text-purple-300" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-veridict-white mb-2">
                Veridict will automatically:
              </h3>
              <ul className="space-y-1 text-sm text-veridict-gray">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
                  Classify each photo (vehicle damage, scene, documents)
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                  Extract damage zones and deformation measurements
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-veridict-lime" />
                  Cross-reference with physics simulation results
                </li>
              </ul>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Navigation buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="flex items-center justify-center gap-4 pt-4"
      >
        <button
          type="button"
          onClick={onBack}
          disabled={isSubmitting}
          className="flex items-center gap-2 px-6 py-3 rounded-xl text-veridict-gray hover:text-veridict-white hover:bg-veridict-green-800/50 transition-all disabled:opacity-50"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>

        <button
          type="button"
          onClick={onSubmit}
          disabled={isSubmitting}
          className="group flex items-center gap-3 px-10 py-5 rounded-2xl font-bold text-xl bg-gradient-to-r from-veridict-lime to-veridict-lime-hover text-veridict-green-900 shadow-xl shadow-veridict-lime/30 hover:shadow-veridict-lime/40 hover:scale-[1.02] transition-all duration-200 disabled:opacity-50 disabled:hover:scale-100"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin" />
              Creating case...
            </>
          ) : (
            <>
              <Sparkles className="w-6 h-6" />
              Generate Expert Report
            </>
          )}
        </button>
      </motion.div>
    </div>
  );
}
