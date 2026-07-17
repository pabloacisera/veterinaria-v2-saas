import { Button } from "@/shared/ui/Button";
import { PaymentMethodSelector } from "@/shared/ui/PaymentMethodSelector";

interface PaymentStepProps {
  paymentMethod: string;
  onPaymentMethodChange: (method: string) => void;
  qrData: string | null;
  onQrDataChange: (data: string | null) => void;
  totalProcedures: number;
  totalSupplies: number;
  grandTotal: number;
  onBack: () => void;
  onNext: () => void;
}

export function PaymentStep({
  paymentMethod,
  onPaymentMethodChange,
  qrData,
  onQrDataChange,
  totalProcedures,
  totalSupplies,
  grandTotal,
  onBack,
  onNext,
}: PaymentStepProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Método de pago</h2>
      <PaymentMethodSelector
        value={paymentMethod}
        onChange={(m) => { onPaymentMethodChange(m); onQrDataChange(null); }}
        qrData={qrData}
      />

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
        <Button onClick={onNext}>Continuar</Button>
      </div>
    </div>
  );
}
