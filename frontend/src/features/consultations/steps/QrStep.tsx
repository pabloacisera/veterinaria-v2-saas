import { Button } from "@/shared/ui/Button";

interface QrStepProps {
  qrData: string;
  onComplete: () => void;
}

export function QrStep({ qrData, onComplete }: QrStepProps) {
  return (
    <div className="space-y-4 text-center">
      <h2 className="text-xl font-bold text-gray-900">Código QR</h2>
      <p className="text-sm text-gray-500">
        Escaneá este código con tu app de Mercado Pago para pagar
      </p>
      <div className="inline-block bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
        <img
          src={`https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(qrData)}`}
          alt="QR de pago"
          className="w-64 h-64"
        />
      </div>
      <div className="flex gap-3 justify-center pt-4">
        <Button onClick={onComplete}>Finalizar</Button>
      </div>
    </div>
  );
}
