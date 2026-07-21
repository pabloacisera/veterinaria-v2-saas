import { useState, useEffect } from "react";
import { Modal } from "@/shared/ui/Modal";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { useCreateSupply, useUpdateSupply } from "@/shared/hooks/useSupplies";
import type { SupplyData, CreateSupplyInput } from "./api";

interface SupplyFormProps {
  open: boolean;
  onClose: () => void;
  supply?: SupplyData | null;
}

export function SupplyForm({ open, onClose, supply }: SupplyFormProps) {
  const createMutation = useCreateSupply();
  const updateMutation = useUpdateSupply();
  const loading = createMutation.isPending || updateMutation.isPending;
  const [form, setForm] = useState<CreateSupplyInput>({
    name: "",
    unit_base: "unidad",
    brand: "",
    description: "",
    unit_price: 0,
    stock_quantity: 0,
    min_stock: 0,
  });

  useEffect(() => {
    if (supply) {
      setForm({
        name: supply.name,
        unit_base: supply.unit_base,
        brand: supply.brand || "",
        description: supply.description || "",
        unit_price: Number(supply.unit_price),
        stock_quantity: Number(supply.stock_quantity),
        min_stock: Number(supply.min_stock),
      });
    } else {
      setForm({
        name: "",
        unit_base: "unidad",
        brand: "",
        description: "",
        unit_price: 0,
        stock_quantity: 0,
        min_stock: 0,
      });
    }
  }, [supply, open]);

  async function handleSubmit() {
    try {
      const payload = {
        ...form,
        brand: form.brand || undefined,
        description: form.description || undefined,
      };
      if (supply) {
        await updateMutation.mutateAsync({ id: supply.id, data: payload });
      } else {
        await createMutation.mutateAsync(payload);
      }
      onClose();
    } catch {
      alert("Error al guardar el insumo");
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={supply ? "Editar insumo" : "Nuevo insumo"}
    >
      <div className="space-y-3">
        <Input
          label="Nombre"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
        <div className="grid grid-cols-2 gap-3">
          <Input
            label="Marca"
            value={form.brand}
            onChange={(e) => setForm({ ...form, brand: e.target.value })}
          />
          <Input
            label="Unidad base"
            value={form.unit_base}
            onChange={(e) => setForm({ ...form, unit_base: e.target.value })}
          />
        </div>
        <Input
          label="Descripción"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
        <div className="grid grid-cols-3 gap-3">
          <Input
            label="Precio unitario"
            type="number"
            step="0.01"
            value={form.unit_price}
            onChange={(e) =>
              setForm({ ...form, unit_price: Number(e.target.value) })
            }
          />
          <Input
            label="Stock"
            type="number"
            step="1"
            value={form.stock_quantity}
            onChange={(e) =>
              setForm({ ...form, stock_quantity: Number(e.target.value) })
            }
          />
          <Input
            label="Stock mínimo"
            type="number"
            step="1"
            value={form.min_stock}
            onChange={(e) =>
              setForm({ ...form, min_stock: Number(e.target.value) })
            }
          />
        </div>
        <div className="flex gap-3 pt-2">
          <Button variant="ghost" onClick={onClose} className="flex-1">
            Cancelar
          </Button>
          <Button
            className="flex-1"
            loading={loading}
            onClick={handleSubmit}
            disabled={!form.name}
          >
            {supply ? "Guardar cambios" : "Crear insumo"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
