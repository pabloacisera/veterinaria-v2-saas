import { Badge } from "@/shared/ui/Badge";

interface SubscriptionStatusProps {
  plan: string;
  status: string;
  endDate: string | null;
  nextBilling: string | null;
}

export function SubscriptionStatus({
  plan,
  status,
  endDate,
  nextBilling,
}: SubscriptionStatusProps) {
  const statusConfig: Record<string, { label: string; variant: "success" | "warning" | "danger" | "default" }> = {
    trial: { label: "Período de prueba", variant: "warning" },
    activa: { label: "Activa", variant: "success" },
    vencida: { label: "Vencida", variant: "danger" },
    bloqueada: { label: "Bloqueada", variant: "danger" },
  };

  const cfg = statusConfig[status] || { label: status, variant: "default" as const };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Suscripción</h3>
        <Badge variant={cfg.variant}>{cfg.label}</Badge>
      </div>
      <div className="grid gap-3 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Plan</span>
          <span className="font-medium capitalize">{plan}</span>
        </div>
        {endDate && (
          <div className="flex justify-between">
            <span className="text-gray-500">Vencimiento</span>
            <span className="font-medium">{new Date(endDate).toLocaleDateString("es-AR")}</span>
          </div>
        )}
        {nextBilling && (
          <div className="flex justify-between">
            <span className="text-gray-500">Próximo cobro</span>
            <span className="font-medium">{new Date(nextBilling).toLocaleDateString("es-AR")}</span>
          </div>
        )}
      </div>
    </div>
  );
}
