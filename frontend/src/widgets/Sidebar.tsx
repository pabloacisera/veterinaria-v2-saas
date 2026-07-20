import { useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  User,
  PawPrint,
  ClipboardList,
  Pill,
  Wallet,
  Globe,
  Bot,
  Store,
  Star,
  Settings,
  MessageCircle,
} from "lucide-react";

const navItems = [
  { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { label: "Clientes", path: "/dashboard/clientes", icon: User },
  { label: "Mascotas", path: "/dashboard/mascotas", icon: PawPrint },
  { label: "Consultas", path: "/dashboard/consultas", icon: ClipboardList },
  { label: "Insumos", path: "/dashboard/insumos", icon: Pill },
  { label: "Caja", path: "/dashboard/caja", icon: Wallet },
  { label: "Comunidad", path: "/dashboard/comunidad", icon: Globe },
  { label: "IA Chat", path: "/dashboard/chat", icon: Bot },
  { label: "Tienda", path: "/dashboard/tienda", icon: Store },
  { label: "Planes", path: "/dashboard/planes", icon: Star },
  { label: "Configuración", path: "/dashboard/configuracion", icon: Settings },
];

const extraItems = [
  { label: "Mensajes Directos", icon: MessageCircle, badge: "Próximamente" },
];

interface SidebarProps {
  onNavigate: (path: string) => void;
}

export function Sidebar({ onNavigate }: SidebarProps) {
  const location = useLocation();

  return (
    <aside className="w-64 bg-white border-r border-gray-100 min-h-screen flex flex-col">
      <div className="p-6">
        <button onClick={() => onNavigate("/dashboard")} className="text-xl font-bold text-primary-600">
          Veter
        </button>
      </div>
      <nav className="flex-1 px-3 space-y-1">
        {navItems.map((item) => {
          const active = location.pathname === item.path;
          return (
            <button
              key={item.path}
              onClick={() => onNavigate(item.path)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? "bg-primary-50 text-primary-700"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >
              <item.icon size={18} />
              {item.label}
            </button>
          );
        })}

        <div className="pt-4 mt-4 border-t border-gray-100">
          {extraItems.map((item) => (
            <div
              key={item.label}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-400 cursor-not-allowed"
            >
              <item.icon size={18} />
              <span className="flex-1">{item.label}</span>
              <span className="text-[10px] bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded-full font-medium">
                {item.badge}
              </span>
            </div>
          ))}
        </div>
      </nav>
    </aside>
  );
}
