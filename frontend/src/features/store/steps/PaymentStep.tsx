import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { PaymentMethodSelector } from "@/shared/ui/PaymentMethodSelector";

interface PaymentStepProps {
  paymentMethod: string;
  onPaymentMethodChange: (method: string) => void;
  qrData: string | null;
  onQrDataChange: (data: string | null) => void;
  notes: string;
  onNotesChange: (value: string) => void;
  subtotal: number;
  IVA: number;
  total: number;
  onBack: () => void;
  onNext: () => void;
}

export function PaymentStep({
  paymentMethod,
  onPaymentMethodChange,
  qrData,
  onQrDataChange,
  notes,
  onNotesChange,
  subtotal,
  IVA,
  total,
  onBack,
  onNext,
}: PaymentStepProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Pago</h2>
      <PaymentMethodSelector
        value={paymentMethod}
        onChange={(m) => { onPaymentMethodChange(m); onQrDataChange(null); }}
        qrData={qrData}
      />
      <Input
        label="Notas (opcional)"
        value={notes}
        onChange={(e) => onNotesChange(e.target.value)}
      />

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

      <div className="flex gap-3 pt-2">
        <Button variant="ghost" onClick={onBack}>Atrás</Button>
        <div className="flex-1" />
        <Button onClick={onNext}>Continuar</Button>
      </div>
    </div>
  );
}
