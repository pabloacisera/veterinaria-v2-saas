import { useNavigate } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Button } from "@/shared/ui/Button";
import { useAuth } from "@/shared/lib/AuthContext";

interface DashboardLayoutProps {
  children: React.ReactNode;
  title: string;
}

export function DashboardLayout({ children, title }: DashboardLayoutProps) {
  const navigate = useNavigate();
  const { logout } = useAuth();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  function handleNavigate(path: string) {
    navigate(path);
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar onNavigate={handleNavigate} />
      <div className="flex-1 flex flex-col">
        <header className="bg-white border-b border-gray-100 px-8 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">{title}</h1>
          <Button variant="ghost" size="sm" onClick={handleLogout}>
            Cerrar sesión
          </Button>
        </header>
        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  );
}
