import { useNavigate } from "react-router-dom";
import { Card } from "@/shared/ui/Card";
import { useClients } from "@/shared/hooks/useClients";
import { usePets } from "@/shared/hooks/usePets";
import { useSubscriptionStatus } from "@/shared/hooks/useSubscriptions";

export function DashboardHome() {
  const navigate = useNavigate();
  const { data: clients = [] } = useClients({ limit: 1 });
  const { data: pets = [] } = usePets({ limit: 1 });
  const { data: sub } = useSubscriptionStatus();

  const clientCount = Array.isArray(clients) ? clients.length : 0;
  const petCount = Array.isArray(pets) ? pets.length : 0;

  const subscriptionWarning =
    sub && (sub.status === "vencida" || sub.status === "bloqueada")
      ? sub.status === "bloqueada"
        ? "Tu suscripción está bloqueada. Renová tu plan para seguir usando el sistema."
        : "Tu suscripción está vencida. Renová tu plan para evitar el bloqueo."
      : null;

  const stats = [
    {
      title: "Clientes",
      value: String(clientCount),
      desc: "Pacientes registrados",
      path: "/dashboard/clientes",
      color: "bg-blue-50 text-blue-700",
    },
    {
      title: "Mascotas",
      value: String(petCount),
      desc: "Animales en el sistema",
      path: "/dashboard/mascotas",
      color: "bg-green-50 text-green-700",
    },
    {
      title: "Consultas",
      value: "—",
      desc: "Atenciones del día",
      path: "/dashboard/consultas",
      color: "bg-purple-50 text-purple-700",
    },
    {
      title: "Caja",
      value: "—",
      desc: "Movimientos de hoy",
      path: "/dashboard/caja",
      color: "bg-amber-50 text-amber-700",
    },
  ];

  const quickActions = [
    {
      label: "Nuevo cliente",
      desc: "Registrar un nuevo cliente",
      path: "/dashboard/clientes",
      icon: "👤",
    },
    {
      label: "Nueva mascota",
      desc: "Agregar una mascota",
      path: "/dashboard/mascotas",
      icon: "🐾",
    },
    {
      label: "Nueva consulta",
      desc: "Iniciar una consulta",
      path: "/dashboard/consultas",
      icon: "📋",
    },
    {
      label: "Nueva venta",
      desc: "Vender insumos",
      path: "/dashboard/tienda",
      icon: "🏪",
    },
  ];

  return (
    <div className="space-y-8">
      {subscriptionWarning && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚠️</span>
            <p className="text-sm text-red-800 font-medium">{subscriptionWarning}</p>
          </div>
          <button
            onClick={() => navigate("/dashboard/planes")}
            className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
          >
            Ver planes
          </button>
        </div>
      )}

      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-gray-500">
          Resumen de tu veterinaria
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <button
            key={stat.title}
            onClick={() => navigate(stat.path)}
            className={`${stat.color} rounded-xl p-5 text-left transition-opacity hover:opacity-80`}
          >
            <p className="text-sm font-medium opacity-75">{stat.title}</p>
            <p className="mt-1 text-3xl font-bold">{stat.value}</p>
            <p className="mt-1 text-xs opacity-60">{stat.desc}</p>
          </button>
        ))}
      </div>

      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-3">
          Acciones rápidas
        </h2>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          {quickActions.map((action) => (
            <button
              key={action.label}
              onClick={() => navigate(action.path)}
              className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm hover:shadow-md transition-shadow text-left"
            >
              <span className="text-2xl">{action.icon}</span>
              <p className="mt-2 font-semibold text-gray-900 text-sm">
                {action.label}
              </p>
              <p className="text-xs text-gray-500">{action.desc}</p>
            </button>
          ))}
        </div>
      </div>

      <Card>
        <h2 className="text-lg font-semibold text-gray-900 mb-2">
          Actividad reciente
        </h2>
        <p className="text-sm text-gray-500">
          Acá vas a ver la actividad reciente de tu veterinaria: consultas,
          ventas y movimientos de caja.
        </p>
      </Card>
    </div>
  );
}

export default DashboardHome;
