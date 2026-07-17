import { useState } from "react";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";

interface Props {
  onSuccess: (token: string, clientName: string) => void;
}

export function ClienteAccesoForm({ onSuccess }: Props) {
  const [accessCode, setAccessCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!accessCode.trim()) {
      setError("Ingresá tu código de acceso");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/v1/cliente/acceso", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ access_code: accessCode.trim() }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Código inválido");
      }
      const data = await res.json();
      onSuccess(data.access_token, data.client_name);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Código de acceso"
        placeholder="Ingresá tu código"
        value={accessCode}
        onChange={(e) => setAccessCode(e.target.value)}
        error={error}
      />
      <Button type="submit" loading={loading} className="w-full">
        Ingresar
      </Button>
    </form>
  );
}
