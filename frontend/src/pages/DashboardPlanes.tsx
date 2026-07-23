import { PlanCard } from "@/features/subscriptions/PlanCard";
import { useInitSubscription } from "@/shared/hooks/useSubscriptions";

const plans = [
  {
    key: "mensual",
    name: "Mensual",
    price: "35.000",
    period: "mes",
    features: [
      "Gestión completa de clientes y mascotas",
      "Consultas y recetas digitales",
      "Control de caja",
      "Tienda de insumos",
      "200 requests/mes al chat IA",
      "1 backup semanal",
      "Soporte en horario de oficina",
    ],
  },
  {
    key: "semestral",
    name: "Semestral",
    price: "180.000",
    period: "6 meses",
    highlighted: true,
    features: [
      "Todo lo del plan Mensual",
      "500 requests/mes al chat IA",
      "Acceso prioritario a features",
      "Ahorrá $30.000 vs el plan mensual",
    ],
  },
  {
    key: "anual",
    name: "Anual",
    price: "420.000",
    period: "12 meses + 3 regalados",
    features: [
      "Todo lo del plan Semestral",
      "Requests ilimitados al agente IA",
      "Atención prioritaria",
      "Facturación electrónica AFIP incluida",
      "Ahorrá $105.000 vs el plan mensual",
    ],
  },
];

export function DashboardPlanes() {
  const initMutation = useInitSubscription();

  async function handleSelect(plan: string) {
    try {
      const result = await initMutation.mutateAsync(plan);
      window.location.href = result.init_point;
    } catch {
      alert("Error al iniciar la suscripción");
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Planes</h1>
        <p className="mt-1 text-gray-500">
          Elegí el plan que mejor se adapte a tu veterinaria
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {plans.map((plan) => (
          <PlanCard
            key={plan.key}
            name={plan.name}
            price={plan.price}
            period={plan.period}
            features={plan.features}
            highlighted={plan.highlighted}
            onSelect={() => handleSelect(plan.key)}
            loading={initMutation.isPending && initMutation.variables === plan.key}
          />
        ))}
      </div>

      <div className="bg-gray-50 rounded-xl p-6 text-sm text-gray-600">
        <p className="font-semibold text-gray-900 mb-1">
          ¿Tenés dudas?
        </p>
        <p>
          Todos los planes incluyen un período de prueba de 3 días sin cargo.
          Podés cancelar cuando quieras. Si necesitás ayuda para elegir,
          escribinos a{" "}
          <a href="mailto:contacto-vet@artisandevs.site" className="text-primary-600 underline">
            contacto-vet@artisandevs.site
          </a>
        </p>
      </div>
    </div>
  );
}

export default DashboardPlanes;
