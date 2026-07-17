import { Button } from "@/shared/ui/Button";
import type { ClientData } from "@/entities/client/types";
import type { PetData } from "@/entities/pet/types";
import type { ProcedureData, SupplyData } from "@/entities/supply/types";

interface ConfirmationStepProps {
  selectedPet: PetData | null;
  selectedClient: ClientData | null;
  reason: string;
  diagnosis: string;
  treatment: string;
  selectedProcedures: { proc: ProcedureData; quantity: number }[];
  selectedSupplies: { supply: SupplyData; quantity: number }[];
  totalProcedures: number;
  totalSupplies: number;
  grandTotal: number;
  loading: boolean;
  onBack: () => void;
  onConfirm: () => void;
}

export function ConfirmationStep({
  selectedPet,
  selectedClient,
  reason,
  diagnosis,
  treatment,
  selectedProcedures,
  selectedSupplies,
  totalProcedures,
  totalSupplies,
  grandTotal,
  loading,
  onBack,
  onConfirm,
}: ConfirmationStepProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Confirmar consulta</h2>

      <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Paciente</span>
          <span className="font-medium">{selectedPet?.name}</span>
        </div>
        {selectedClient && (
          <div className="flex justify-between">
            <span className="text-gray-500">Dueño</span>
            <span>{selectedClient.name} {selectedClient.surname}</span>
          </div>
        )}
        <div className="flex justify-between">
          <span className="text-gray-500">Motivo</span>
          <span>{reason}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Diagnóstico</span>
          <span>{diagnosis}</span>
        </div>
        {treatment && (
          <div className="flex justify-between">
            <span className="text-gray-500">Tratamiento</span>
            <span>{treatment}</span>
          </div>
        )}
      </div>

      {selectedProcedures.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Procedimientos</h3>
          <div className="border border-gray-100 rounded-lg divide-y divide-gray-50">
            {selectedProcedures.map((item, i) => (
              <div key={i} className="flex justify-between px-4 py-2 text-sm">
                <span>{item.proc.name} x{item.quantity}</span>
                <span>${(item.quantity * Number(item.proc.price)).toLocaleString("es-AR")}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedSupplies.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Insumos</h3>
          <div className="border border-gray-100 rounded-lg divide-y divide-gray-50">
            {selectedSupplies.map((item, i) => (
              <div key={i} className="flex justify-between px-4 py-2 text-sm">
                <span>{item.supply.name} x{item.quantity}</span>
                <span>${(item.quantity * Number(item.supply.unit_price)).toLocaleString("es-AR")}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-4 space-y-1 text-sm">
        {totalProcedures > 0 && (
          <div className="flex justify-between">
            <span className="text-gray-500">Total procedimientos</span>
            <span>${totalProcedures.toLocaleString("es-AR")}</span>
          </div>
        )}
        {totalSupplies > 0 && (
          <div className="flex justify-between">
            <span className="text-gray-500">Total insumos</span>
            <span>${totalSupplies.toLocaleString("es-AR")}</span>
          </div>
        )}
        <div className="flex justify-between font-bold text-base pt-1 border-t border-gray-200">
          <span>Total</span>
          <span>${grandTotal.toLocaleString("es-AR")}</span>
        </div>
      </div>

      <div className="flex gap-3 pt-2">
        <Button variant="ghost" onClick={onBack}>Atrás</Button>
        <div className="flex-1" />
        <Button loading={loading} onClick={onConfirm}>
          Confirmar consulta
        </Button>
      </div>
    </div>
  );
}
