"use client";

import type { CalculoFisico } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface CalculosFisicosProps {
  calculos: CalculoFisico[];
}

export function CalculosFisicos({ calculos }: CalculosFisicosProps) {
  if (calculos.length === 0) {
    return (
      <div className="p-6 text-center text-muted-foreground">
        No hay calculos disponibles
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <h3 className="font-semibold">Calculos Fisicos</h3>
      <div className="grid gap-4">
        {calculos.map((calculo, index) => (
          <Card key={index}>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">{calculo.nombre}</CardTitle>
              <CardDescription className="font-mono text-xs">
                {calculo.formula}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {calculo.valor.toFixed(2)} {calculo.unidad}
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                {calculo.justificacion}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
