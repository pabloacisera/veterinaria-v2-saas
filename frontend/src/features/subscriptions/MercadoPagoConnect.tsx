import { useState } from "react";
import { Button } from "@/shared/ui/Button";
import { Badge } from "@/shared/ui/Badge";
import { useOAuthStatus } from "@/shared/hooks/useSubscriptions";
import { initOAuth } from "./api";

export function MercadoPagoConnect() {
  const { data: status, isLoading: loading } = useOAuthStatus();
  const [connecting, setConnecting] = useState(false);

  async function handleConnect() {
    setConnecting(true);
    try {
      const data = await initOAuth();
      window.location.href = data.auth_url;
    } catch {
      alert("Error al iniciar conexión con Mercado Pago");
      setConnecting(false);
    }
  }

  if (loading) return <div className="text-sm text-gray-400">Cargando...</div>;

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Mercado Pago</h3>
        <Badge variant={status?.conectado ? "success" : "warning"}>
          {status?.conectado ? "Conectado" : "Desconectado"}
        </Badge>
      </div>
      <p className="text-sm text-gray-500">
        Conectá tu cuenta de Mercado Pago para cobrarle a tus clientes con transferencia o QR.
      </p>
      {status?.conectado ? (
        <p className="text-sm text-gray-700">
          Cuenta conectada: <span className="font-mono">{status.mp_user_id}</span>
        </p>
      ) : (
        <Button onClick={handleConnect} loading={connecting}>
          Conectar Mercado Pago
        </Button>
      )}
    </div>
  );
}
