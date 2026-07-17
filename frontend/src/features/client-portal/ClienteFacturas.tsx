import { Card } from "@/shared/ui/Card";
import { Button } from "@/shared/ui/Button";
import type { Factura } from "@/entities/client-portal";

interface Props {
  facturas: Factura[];
  loading: boolean;
}

export function ClienteFacturas({ facturas, loading }: Props) {
  if (loading) {
    return <p className="text-gray-500">Cargando facturas...</p>;
  }

  if (facturas.length === 0) {
    return <p className="text-gray-500">No hay facturas disponibles.</p>;
  }

  return (
    <div className="space-y-3">
      {facturas.map((f) => (
        <Card key={f.id} className="p-4 flex items-center justify-between">
          <div>
            <p className="font-medium text-gray-900">
              Factura #{f.version} - {f.entity_type === "consulta" ? "Consulta" : "Tienda"}
            </p>
            <p className="text-sm text-gray-500">{new Date(f.created_at).toLocaleDateString()}</p>
            {f.pending_payment && (
              <p className="text-sm text-amber-600 font-medium mt-1">
                Pago pendiente: ${f.pending_payment.amount.toFixed(2)}
              </p>
            )}
          </div>
          {f.download_url && (
            <Button variant="outline" size="sm" onClick={() => window.open(f.download_url!, "_blank")}>
              Descargar
            </Button>
          )}
        </Card>
      ))}
    </div>
  );
}
