import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import type { SupplyData } from "@/entities/supply/types";

interface SuppliesStepProps {
  supplySearch: string;
  onSupplySearchChange: (value: string) => void;
  filteredSupplies: SupplyData[];
  selectedSupplies: { supply: SupplyData; quantity: number }[];
  onAddSupply: (supply: SupplyData) => void;
  onRemoveSupply: (index: number) => void;
  onSupplyQuantityChange: (index: number, quantity: number) => void;
  onBack: () => void;
  onNext: () => void;
}

export function SuppliesStep({
  supplySearch,
  onSupplySearchChange,
  filteredSupplies,
  selectedSupplies,
  onAddSupply,
  onRemoveSupply,
  onSupplyQuantityChange,
  onBack,
  onNext,
}: SuppliesStepProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Insumos</h2>

      <Input
        label="Agregar insumo"
        placeholder="Buscar..."
        value={supplySearch}
        onChange={(e) => onSupplySearchChange(e.target.value)}
      />

      {supplySearch && (
        <div className="max-h-40 overflow-y-auto border border-gray-100 rounded-lg divide-y divide-gray-50">
          {filteredSupplies.slice(0, 8).map((s) => (
            <button
              key={s.id}
              onClick={() => onAddSupply(s)}
              className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex justify-between"
            >
              <span className="font-medium">{s.name}</span>
              <span className="text-gray-400">
                ${Number(s.unit_price).toLocaleString("es-AR")} / {s.unit_base}
              </span>
            </button>
          ))}
          {filteredSupplies.length === 0 && (
            <p className="px-3 py-2 text-sm text-gray-400">Sin resultados</p>
          )}
        </div>
      )}

      {selectedSupplies.length > 0 && (
        <div className="border border-gray-100 rounded-lg divide-y divide-gray-50">
          {selectedSupplies.map((item, i) => (
            <div key={i} className="flex items-center justify-between px-4 py-3">
              <div>
                <p className="text-sm font-medium">{item.supply.name}</p>
                <p className="text-xs text-gray-400">
                  ${Number(item.supply.unit_price).toLocaleString("es-AR")} / {item.supply.unit_base}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <input
                  type="number"
                  min="1"
                  step="1"
                  value={item.quantity}
                  onChange={(e) => onSupplyQuantityChange(i, Number(e.target.value))}
                  className="w-16 rounded border border-gray-300 px-2 py-1 text-sm text-center"
                />
                <span className="text-sm font-medium w-20 text-right">
                  ${(item.quantity * Number(item.supply.unit_price)).toLocaleString("es-AR")}
                </span>
                <button
                  onClick={() => onRemoveSupply(i)}
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
