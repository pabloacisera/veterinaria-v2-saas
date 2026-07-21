import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/shared/ui/Card";
import { RegisterForm } from "@/features/auth/RegisterForm";
import { ActivateForm } from "@/features/auth/ActivateForm";

export function Register() {
  const navigate = useNavigate();
  const [registeredEmail, setRegisteredEmail] = useState<string | null>(null);

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8 bg-gray-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <button
            onClick={() => navigate("/")}
            className="text-2xl font-bold text-primary-600"
          >
            Veter
          </button>
        </div>

        <Card>
          {registeredEmail ? (
            <>
              <h1 className="text-xl font-bold text-gray-900 mb-6">
                Activá tu cuenta
              </h1>
              <ActivateForm email={registeredEmail} />
            </>
          ) : (
            <>
              <h1 className="text-xl font-bold text-gray-900 mb-6">
                Crear cuenta
              </h1>
              <RegisterForm onSuccess={setRegisteredEmail} />
            </>
          )}
        </Card>
      </div>
    </div>
  );
}
