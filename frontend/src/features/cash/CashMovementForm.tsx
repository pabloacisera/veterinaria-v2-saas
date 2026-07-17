import { useState } from "react";
import { Modal } from "@/shared/ui/Modal";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { useCreateMovement } from "@/shared/hooks/useCash";
import type { CreateMovementInput } from "./api";

interface CashMovementFormProps {
  open: boolean;
  onClose: () => void;
}

export function CashMovementForm({ open, onClose }: CashMovementFormProps) {
  const createMutation = useCreateMovement();
  const loading = createMutation.isPending;
  const [form, setForm] = useState<CreateMovementInput>({
    movement_type: "income",
    amount: 0,
    category: "",
    description: "",
    payment_method: "efectivo",
    status: "pagado",
  });

  async function handleSubmit() {
    try {
      await createMutation.mutateAsync({
        ...form,
        category: form.category || undefined,
        description: form.description || undefined,
        amount: form.amount || 0,
      });
      onClose();
    } catch {
      alert("Error al registrar el movimiento");
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Nuevo movimiento">
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo
            </label>
            <select
              value={form.movement_type}
              onChange={(e) =>
                setForm({
                  ...form,
                  movement_type: e.target.value as "income" | "expense",
                })
              }
              className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="income">Ingreso</option>
              <option value="expense">Egreso</option>
            </select>
          </div>
          <Input
            label="Monto"
            type="number"
            step="0.01"
            value={form.amount}
            onChange={(e) =>
              setForm({ ...form, amount: Number(e.target.value) })
            }
          />
        </div>
        <Input
          label="Categoría"
          value={form.category}
          onChange={(e) => setForm({ ...form, category: e.target.value })}
        />
        <Input
          label="Descripción"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Método de pago
            </label>
            <select
              value={form.payment_method}
              onChange={(e) =>
                setForm({ ...form, payment_method: e.target.value })
              }
              className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="efectivo">Efectivo</option>
              <option value="transferencia">Transferencia</option>
              <option value="tarjeta">Tarjeta</option>
              <option value="mercadopago">Mercado Pago</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estado
            </label>
            <select
              value={form.status}
              onChange={(e) =>
                setForm({
                  ...form,
                  status: e.target.value as "pagado" | "pendiente",
                })
              }
              className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="pagado">Pagado</option>
              <option value="pendiente">Pendiente</option>
            </select>
          </div>
        </div>
        <div className="flex gap-3 pt-2">
          <Button variant="ghost" onClick={onClose} className="flex-1">
            Cancelar
          </Button>
          <Button
            className="flex-1"
            loading={loading}
            onClick={handleSubmit}
            disabled={!form.amount || form.amount <= 0}
          >
            Registrar movimiento
          </Button>
        </div>
      </div>
    </Modal>
  );
}
