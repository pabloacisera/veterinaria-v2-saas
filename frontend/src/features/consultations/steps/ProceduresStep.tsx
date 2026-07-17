import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import type { ProcedureData } from "@/entities/supply/types";

interface ProceduresStepProps {
  procedureSearch: string;
  onProcedureSearchChange: (value: string) => void;
  filteredProcedures: ProcedureData[];
  selectedProcedures: { proc: ProcedureData; quantity: number }[];
  onAddProcedure: (proc: ProcedureData) => void;
  onRemoveProcedure: (index: number) => void;
  onProcedureQuantityChange: (index: number, quantity: number) => void;
  onBack: () => void;
  onNext: () => void;
}

export function ProceduresStep({
  procedureSearch,
  onProcedureSearchChange,
  filteredProcedures,
  selectedProcedures,
  onAddProcedure,
  onRemoveProcedure,
  onProcedureQuantityChange,
  onBack,
  onNext,
}: ProceduresStepProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Procedimientos</h2>

      <Input
        label="Agregar procedimiento"
        placeholder="Buscar..."
        value={procedureSearch}
        onChange={(e) => onProcedureSearchChange(e.target.value)}
      />

      {procedureSearch && (
        <div className="max-h-40 overflow-y-auto border border-gray-100 rounded-lg divide-y divide-gray-50">
          {filteredProcedures.slice(0, 8).map((p) => (
            <button
              key={p.id}
              onClick={() => onAddProcedure(p)}
              className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex justify-between"
            >
              <span className="font-medium">{p.name}</span>
              <span className="text-gray-400">
                ${Number(p.price).toLocaleString("es-AR")}
              </span>
            </button>
          ))}
          {filteredProcedures.length === 0 && (
            <p className="px-3 py-2 text-sm text-gray-400">Sin resultados</p>
          )}
        </div>
      )}

      {selectedProcedures.length > 0 && (
        <div className="border border-gray-100 rounded-lg divide-y divide-gray-50">
          {selectedProcedures.map((item, i) => (
            <div key={i} className="flex items-center justify-between px-4 py-3">
              <div>
                <p className="text-sm font-medium">{item.proc.name}</p>
                <p className="text-xs text-gray-400">
                  ${Number(item.proc.price).toLocaleString("es-AR")} c/u
                </p>
              </div>
              <div className="flex items-center gap-3">
                <input
                  type="number"
                  min="1"
                  value={item.quantity}
                  onChange={(e) => onProcedureQuantityChange(i, Number(e.target.value))}
                  className="w-16 rounded border border-gray-300 px-2 py-1 text-sm text-center"
                />
                <span className="text-sm font-medium w-20 text-right">
                  ${(item.quantity * Number(item.proc.price)).toLocaleString("es-AR")}
                </span>
                <button
                  onClick={() => onRemoveProcedure(i)}
                  className="text-red-500 hover:text-red-700 text-sm"
                >
                  Quitar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-3 pt-2">
        <Button variant="ghost" onClick={onBack}>Atrás</Button>
        <div className="flex-1" />
        <Button onClick={onNext}>Continuar</Button>
      </div>
    </div>
  );
}
