import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import type { SupplyData } from "@/entities/supply/types";

interface LineItem {
  supply: SupplyData;
  quantity: number;
}

interface ItemsStepProps {
  supplySearch: string;
  onSupplySearchChange: (value: string) => void;
  filteredSupplies: SupplyData[];
  selectedSupply: SupplyData | null;
  onSelectSupply: (supply: SupplyData) => void;
  itemQuantity: number;
  onItemQuantityChange: (value: number) => void;
  onAddItem: () => void;
  items: LineItem[];
  onRemoveItem: (index: number) => void;
  onBack: () => void;
  onNext: () => void;
}

export function ItemsStep({
  supplySearch,
  onSupplySearchChange,
  filteredSupplies,
  selectedSupply,
  onSelectSupply,
  itemQuantity,
  onItemQuantityChange,
  onAddItem,
  items,
  onRemoveItem,
  onBack,
  onNext,
}: ItemsStepProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Insumos</h2>

      <div className="flex gap-2 items-end">
        <div className="flex-1">
          <Input
            label="Buscar insumo"
            placeholder="Escribí para buscar..."
            value={supplySearch}
            onChange={(e) => {
              onSupplySearchChange(e.target.value);
            }}
          />
        </div>
        {selectedSupply && (
          <div className="w-24">
            <Input
              label="Cant."
              type="number"
              min="1"
              step="1"
              value={itemQuantity}
              onChange={(e) => onItemQuantityChange(Number(e.target.value))}
            />
          </div>
        )}
        {selectedSupply && (
          <Button size="sm" onClick={onAddItem}>Agregar</Button>
        )}
      </div>

      {supplySearch && !selectedSupply && (
        <div className="max-h-40 overflow-y-auto border border-gray-100 rounded-lg divide-y divide-gray-50">
          {filteredSupplies.slice(0, 8).map((s) => (
            <button
              key={s.id}
              onClick={() => onSelectSupply(s)}
              className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition-colors"
            >
              <span className="font-medium">{s.name}</span>
              {s.brand && <span className="text-gray-400 ml-2">{s.brand}</span>}
              <span className="text-gray-400 ml-2">
                ${Number(s.unit_price).toLocaleString("es-AR")} / {s.unit_base}
              </span>
            </button>
          ))}
          {filteredSupplies.length === 0 && (
            <p className="px-3 py-2 text-sm text-gray-400">Sin resultados</p>
          )}
        </div>
      )}

      {items.length > 0 && (
        <div className="border border-gray-100 rounded-lg divide-y divide-gray-50">
          {items.map((item, i) => (
            <div key={i} className="flex items-center justify-between px-4 py-3">
              <div>
                <p className="text-sm font-medium text-gray-900">{item.supply.name}</p>
                <p className="text-xs text-gray-400">
                  {item.quantity} x ${Number(item.supply.unit_price).toLocaleString("es-AR")}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium">
                  ${(item.quantity * Number(item.supply.unit_price)).toLocaleString("es-AR")}
                </span>
                <button
                  onClick={() => onRemoveItem(i)}
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
        <Button onClick={onNext} disabled={items.length === 0}>Continuar</Button>
      </div>
    </div>
  );
}
