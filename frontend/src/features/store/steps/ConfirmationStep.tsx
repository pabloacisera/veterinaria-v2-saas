import { Button } from "@/shared/ui/Button";
import type { SupplyData } from "@/entities/supply/types";

interface LineItem {
  supply: SupplyData;
  quantity: number;
}

interface ConfirmationStepProps {
  clientName: string;
  paymentMethod: string;
  items: LineItem[];
  subtotal: number;
  IVA: number;
  total: number;
  notes: string;
  loading: boolean;
  onBack: () => void;
  onConfirm: () => void;
}

export function ConfirmationStep({
  clientName,
  paymentMethod,
  items,
  subtotal,
  IVA,
  total,
  notes,
  loading,
  onBack,
  onConfirm,
}: ConfirmationStepProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Confirmar venta</h2>

      <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Cliente</span>
          <span>{clientName || "Venta al público"}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Método de pago</span>
          <span className="capitalize">{paymentMethod}</span>
        </div>
      </div>

      <div className="border border-gray-100 rounded-lg divide-y divide-gray-50">
        {items.map((item, i) => (
          <div key={i} className="flex justify-between px-4 py-2 text-sm">
            <span>{item.supply.name} x{item.quantity}</span>
            <span>${(item.quantity * Number(item.supply.unit_price)).toLocaleString("es-AR")}</span>
          </div>
        ))}
      </div>

      <div className="bg-gray-50 rounded-lg p-4 space-y-1 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Subtotal</span>
          <span>${subtotal.toLocaleString("es-AR")}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">IVA (21%)</span>
          <span>${IVA.toLocaleString("es-AR")}</span>
        </div>
        <div className="flex justify-between font-bold text-base pt-1 border-t border-gray-200">
          <span>Total</span>
          <span>${total.toLocaleString("es-AR")}</span>
        </div>
      </div>

      {notes && (
        <p className="text-sm text-gray-500">
          <span className="font-medium">Notas:</span> {notes}
        </p>
      )}

      <div className="flex gap-3 pt-2">
        <Button variant="ghost" onClick={onBack}>Atrás</Button>
        <div className="flex-1" />
        <Button loading={loading} onClick={onConfirm}>Confirmar venta</Button>
      </div>
    </div>
  );
}
