import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ClienteLayout } from "./ClienteLayout";
import { ClienteDashboard } from "@/features/client-portal/ClienteDashboard";

export function ClienteInicio() {
  const navigate = useNavigate();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("client_token");
    if (!token) {
      navigate("/cliente/acceso");
      return;
    }
    setChecking(false);
  }, [navigate]);

  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Cargando...</p>
      </div>
    );
  }

  return (
    <ClienteLayout>
      <ClienteDashboard />
    </ClienteLayout>
  );
}

export default ClienteInicio;
