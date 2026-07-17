import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { registerUser } from "./api";

interface RegisterFormProps {
  onSuccess: (email: string) => void;
}

type FieldErrors = Record<string, string>;

export function RegisterForm({ onSuccess }: RegisterFormProps) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});

  function validate(form: FormData): Record<string, string> | null {
    const errors: FieldErrors = {};
    const name = form.get("name") as string;
    const surname = form.get("surname") as string;
    const email = form.get("email") as string;
    const password = form.get("password") as string;
    const company = form.get("company_name") as string;
    const cuit = form.get("cuit") as string;

    if (!name?.trim()) errors.name = "El nombre es obligatorio";
    if (!surname?.trim()) errors.surname = "El apellido es obligatorio";
    if (!email?.trim()) errors.email = "El email es obligatorio";
    else if (!/\S+@\S+\.\S+/.test(email))
      errors.email = "Email inválido";
    if (!password) errors.password = "La contraseña es obligatoria";
    else if (password.length < 6)
      errors.password = "Mínimo 6 caracteres";
    if (!company?.trim()) errors.company_name = "El nombre de la empresa es obligatorio";
    if (!cuit?.trim()) errors.cuit = "El CUIT es obligatorio";

    return Object.keys(errors).length ? errors : null;
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setServerError("");
    setFieldErrors({});

    const form = new FormData(e.currentTarget);
    const validation = validate(form);
    if (validation) {
      setFieldErrors(validation);
      return;
    }

    setLoading(true);
    try {
      await registerUser({
        name: form.get("name") as string,
        surname: form.get("surname") as string,
        email: form.get("email") as string,
        password: form.get("password") as string,
        company_name: form.get("company_name") as string,
        cuit: form.get("cuit") as string,
      });
      onSuccess(form.get("email") as string);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Error al registrarse";
      setServerError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {serverError && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
          {serverError}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <Input
          name="name"
          label="Nombre"
          placeholder="Juan"
          error={fieldErrors.name}
        />
        <Input
          name="surname"
          label="Apellido"
          placeholder="Pérez"
          error={fieldErrors.surname}
        />
      </div>

      <Input
        name="email"
        label="Email"
        type="email"
        placeholder="juan@ejemplo.com"
        error={fieldErrors.email}
      />

      <Input
        name="password"
        label="Contraseña"
        type="password"
        placeholder="••••••••"
        error={fieldErrors.password}
      />

      <Input
        name="company_name"
        label="Nombre de la empresa"
        placeholder="Veterinaria San Martín"
        error={fieldErrors.company_name}
      />

      <Input
        name="cuit"
        label="CUIT"
        placeholder="20-12345678-9"
        error={fieldErrors.cuit}
      />

      <Button type="submit" loading={loading} className="w-full" size="lg">
        Crear cuenta
      </Button>

      <p className="text-center text-sm text-gray-500">
        ¿Ya tenés cuenta?{" "}
        <button
          type="button"
          onClick={() => navigate("/login")}
          className="font-semibold text-primary-600 hover:text-primary-700"
        >
          Iniciar sesión
        </button>
      </p>
    </form>
  );
}
