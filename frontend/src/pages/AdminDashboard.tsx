import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AdminCompanyList } from "@/features/admin/AdminCompanyList";
import { AdminCompanyDetail } from "@/features/admin/AdminCompanyDetail";
import { AdminBackupPanel } from "@/features/admin/AdminBackupPanel";
import { AdminExportPanel } from "@/features/admin/AdminExportPanel";
import { Button } from "@/shared/ui/Button";
import type { CompanyAdmin } from "@/features/admin/api";

type Section = "companias" | "backups" | "exportar";

const navItems: { key: Section; label: string; icon: string }[] = [
  { key: "companias", label: "Compañías", icon: "🏢" },
  { key: "backups", label: "Backups", icon: "💾" },
  { key: "exportar", label: "Exportar", icon: "📥" },
];

export function AdminDashboard() {
  const navigate = useNavigate();
  const [section, setSection] = useState<Section>("companias");
  const [selectedCompany, setSelectedCompany] = useState<CompanyAdmin | null>(
    null
  );

  useEffect(() => {
    const token = localStorage.getItem("admin_token");
    if (!token) {
      navigate("/access_role/admin/developer");
    }
  }, [navigate]);

  function handleLogout() {
    if (import.meta.env.PROD) {
      fetch("/access_role/admin/developer/logout", { method: "POST" }).catch(() => {});
    }
    localStorage.removeItem("admin_token");
    navigate("/access_role/admin/developer");
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-64 bg-gray-900 min-h-screen flex flex-col">
        <div className="p-6">
          <h1 className="text-xl font-bold text-white">Admin Veter</h1>
        </div>
        <nav className="flex-1 px-3 space-y-1">
          {navItems.map((item) => (
            <button
              key={item.key}
              onClick={() => setSection(item.key)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                section === item.key
                  ? "bg-indigo-600 text-white"
                  : "text-gray-300 hover:bg-gray-800 hover:text-white"
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
        <div className="p-3 border-t border-gray-800">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="w-full text-gray-400 hover:text-white justify-start"
          >
            Cerrar sesión
          </Button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col">
        <header className="bg-white border-b border-gray-100 px-8 py-4">
          <h1 className="text-xl font-bold text-gray-900">
            {navItems.find((n) => n.key === section)?.label}
          </h1>
        </header>
        <main className="flex-1 p-8">
          {section === "companias" && (
            <AdminCompanyList onSelect={setSelectedCompany} />
          )}
          {section === "backups" && <AdminBackupPanel />}
          {section === "exportar" && <AdminExportPanel />}
        </main>
      </div>

      <AdminCompanyDetail
        company={selectedCompany}
        onClose={() => setSelectedCompany(null)}
        onSuccess={() => setSelectedCompany(null)}
      />
    </div>
  );
}

export default AdminDashboard;
