import { useNavigate } from "react-router-dom";
import { Button } from "@/shared/ui/Button";

interface Props {
  children: React.ReactNode;
}

export function ClienteLayout({ children }: Props) {
  const navigate = useNavigate();

  function handleLogout() {
    if (import.meta.env.PROD) {
      fetch("/api/v1/cliente/logout", { method: "POST" }).catch(() => {});
    }
    localStorage.removeItem("client_token");
    navigate("/cliente/acceso");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-100 px-8 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Portal del Cliente</h1>
        <Button variant="ghost" size="sm" onClick={handleLogout}>
          Cerrar sesión
        </Button>
      </header>
      <main className="max-w-5xl mx-auto p-8">{children}</main>
    </div>
  );
}
