import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { loginUser } from "./api";

interface LoginFormProps {
  onSuccess: (token: string, expiresIn?: number) => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");

    const form = new FormData(e.currentTarget);
    const email = form.get("email") as string;
    const password = form.get("password") as string;

    if (!email || !password) {
      setError("Completá todos los campos");
      return;
    }

    setLoading(true);
    try {
      const result = await loginUser({ email, password });
      onSuccess(result.access_token, result.expires_in);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Error al iniciar sesión";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <Input
        name="email"
        label="Email"
        type="email"
        placeholder="juan@ejemplo.com"
      />

      <Input
        name="password"
        label="Contraseña"
        type="password"
        placeholder="••••••••"
      />

      <Button type="submit" loading={loading} className="w-full" size="lg">
        Iniciar sesión
      </Button>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-300" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="bg-white px-2 text-gray-500">O continuá con</span>
        </div>
      </div>

      <button
        type="button"
        onClick={() => {
          window.location.href = "https://dev-api.artisandevs.site/api/v1/auth/google";
        }}
        className="flex w-full items-center justify-center gap-3 rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 transition-colors"
      >
        <svg className="h-5 w-5" viewBox="0 0 24 24">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
        </svg>
        Google
      </button>

      <p className="text-center text-sm text-gray-500">
        ¿No tenés cuenta?{" "}
        <button
          type="button"
          onClick={() => navigate("/register")}
          className="font-semibold text-primary-600 hover:text-primary-700"
        >
          Registrarse
        </button>
      </p>
    </form>
  );
}
