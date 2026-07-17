import { useState } from "react";
import { Modal } from "@/shared/ui/Modal";
import { Button } from "@/shared/ui/Button";
import { Input } from "@/shared/ui/Input";
import { useGrantFreeSubscription } from "@/shared/hooks/useAdmin";
import type { CompanyAdmin } from "./api";

interface AdminCompanyDetailProps {
  company: CompanyAdmin | null;
  onClose: () => void;
}

export function AdminCompanyDetail({
  company,
  onClose,
}: AdminCompanyDetailProps) {
  const grantMutation = useGrantFreeSubscription();
  const [dias, setDias] = useState("");
  const [message, setMessage] = useState("");

  if (!company) return null;

  async function handleGrantSubscription() {
    const numDias = parseInt(dias, 10);
    if (!numDias || numDias <= 0) return;

    setMessage("");
    try {
      const res = await grantMutation.mutateAsync({ companyId: company.id, dias: numDias });
      setMessage(res.message);
      setDias("");
    } catch (err) {
      setMessage(
        err instanceof Error ? err.message : "Error al extender suscripción"
      );
    }
  }

  return (
    <Modal open={!!company} onClose={onClose} title="Detalle de Compañía">
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-gray-500 font-medium">CUIT</p>
            <p className="text-sm text-gray-900">{company.cuit || "—"}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 font-medium">Nombre</p>
            <p className="text-sm text-gray-900">{company.nombre}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 font-medium">Plan</p>
            <p className="text-sm text-gray-900">{company.plan || "—"}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 font-medium">Estado</p>
            <p className="text-sm text-gray-900">{company.estado || "—"}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 font-medium">Inicio Suscripción</p>
            <p className="text-sm text-gray-900">
              {company.inicio_suscripcion
                ? new Date(company.inicio_suscripcion).toLocaleDateString()
                : "—"}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 font-medium">Fin Suscripción</p>
            <p className="text-sm text-gray-900">
              {company.fin_suscripcion
                ? new Date(company.fin_suscripcion).toLocaleDateString()
                : "—"}
            </p>
          </div>
        </div>

        <div className="border-t border-gray-100 pt-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">
            Extender suscripción gratuita
          </h3>
          <div className="flex gap-2 items-end">
            <div className="flex-1">
              <Input
                label="Días"
                type="number"
                min="1"
                placeholder="30"
                value={dias}
                onChange={(e) => setDias(e.target.value)}
              />
            </div>
            <Button
              onClick={handleGrantSubscription}
              loading={grantMutation.isPending}
              disabled={!dias || parseInt(dias) <= 0}
            >
              Extender
            </Button>
          </div>
          {message && (
            <p
              className={`mt-2 text-sm ${
                message.includes("Error") || message.includes("error")
                  ? "text-red-600"
                  : "text-green-600"
              }`}
            >
              {message}
            </p>
          )}
        </div>
      </div>
    </Modal>
  );
}
