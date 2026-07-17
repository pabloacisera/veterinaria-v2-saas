import { useNavigate } from "react-router-dom";
import { Card } from "@/shared/ui/Card";
import { ClienteAccesoForm } from "@/features/client-portal/ClienteAccesoForm";

export function ClienteAcceso() {
  const navigate = useNavigate();

  function handleSuccess(token: string, _clientName: string) {
    localStorage.setItem("client_token", token);
    navigate("/cliente/inicio");
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gray-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-primary-600">Veter</h1>
          <p className="mt-2 text-gray-500">Portal del Cliente</p>
        </div>
        <Card>
          <h2 className="text-xl font-bold text-gray-900 mb-6">Acceder</h2>
          <ClienteAccesoForm onSuccess={handleSuccess} />
        </Card>
      </div>
    </div>
  );
}
