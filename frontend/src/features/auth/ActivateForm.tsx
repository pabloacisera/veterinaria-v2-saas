import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { activateAccount } from "./api";

interface ActivateFormProps {
  email: string;
}

export function ActivateForm({ email }: ActivateFormProps) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");

    const form = new FormData(e.currentTarget);
    const code = form.get("code") as string;

    if (!code || code.length !== 6) {
      setError("Ingresá el código de 6 dígitos");
      return;
    }

    setLoading(true);
    try {
      await activateAccount({ email, code });
      navigate("/login?activated=true");
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Error al activar la cuenta";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="text-center text-sm text-gray-600 mb-4">
        <p>
          Enviamos un código de activación a{" "}
          <strong className="text-gray-900">{email}</strong>
        </p>
        <p className="mt-1">Revisá tu bandeja de entrada y colocá el código abajo.</p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <Input
        name="code"
        label="Código de activación"
        placeholder="123456"
        maxLength={6}
        className="text-center text-2xl tracking-[0.5em] font-mono"
        autoComplete="one-time-code"
      />

      <Button type="submit" loading={loading} className="w-full" size="lg">
        Activar cuenta
      </Button>

      <p className="text-center text-sm text-gray-500">
        ¿No recibiste el código?{" "}
        <button
          type="button"
          onClick={() => navigate("/register")}
          className="font-semibold text-primary-600 hover:text-primary-700"
        >
          Reintentar registro
        </button>
      </p>
    </form>
  );
}
