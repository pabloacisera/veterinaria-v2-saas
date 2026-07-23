import { SubscriptionStatus } from "@/features/subscriptions/SubscriptionStatus";
import { MercadoPagoConnect } from "@/features/subscriptions/MercadoPagoConnect";
import { useSubscriptionStatus } from "@/shared/hooks/useSubscriptions";

export function DashboardConfiguracion() {
  const { data: sub } = useSubscriptionStatus();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configuración</h1>
        <p className="mt-1 text-gray-500">
          Administrá tu suscripción y conexiones
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {sub && (
          <SubscriptionStatus
            plan={sub.plan}
            status={sub.status}
            endDate={sub.end_date}
            nextBilling={sub.next_billing_date}
          />
        )}
        <MercadoPagoConnect />
      </div>
    </div>
  );
}

export default DashboardConfiguracion;
