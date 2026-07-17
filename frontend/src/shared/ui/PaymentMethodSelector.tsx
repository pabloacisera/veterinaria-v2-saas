interface PaymentMethodSelectorProps {
  value: string;
  onChange: (method: string) => void;
  qrData?: string | null;
}

export function PaymentMethodSelector({
  value,
  onChange,
  qrData,
}: PaymentMethodSelectorProps) {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Método de pago
        </label>
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="efectivo">Efectivo</option>
          <option value="transferencia">Transferencia</option>
          <option value="qr">QR (Mercado Pago)</option>
        </select>
      </div>

      {value === "qr" && qrData && (
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <p className="text-sm text-gray-500 mb-2">
            Escaneá este código QR para pagar
          </p>
          <div className="inline-block bg-white p-3 rounded-lg border border-gray-200">
            <img
              src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrData)}`}
              alt="Código QR de pago"
              className="w-48 h-48"
            />
          </div>
          <p className="text-xs text-gray-400 mt-2">
            O pagá desde tu app de Mercado Pago
          </p>
        </div>
      )}

      {value === "qr" && !qrData && (
        <p className="text-sm text-gray-400">
          El código QR se generará al confirmar la operación.
        </p>
      )}
    </div>
  );
}
