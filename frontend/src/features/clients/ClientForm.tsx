import { useState, useEffect } from "react";
import { Modal } from "@/shared/ui/Modal";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { useCreateClient, useUpdateClient } from "@/shared/hooks/useClients";
import type { ClientData, CreateClientInput } from "./api";

interface ClientFormProps {
  open: boolean;
  onClose: () => void;
  client?: ClientData | null;
}

export function ClientForm({
  open,
  onClose,
  client,
}: ClientFormProps) {
  const createMutation = useCreateClient();
  const updateMutation = useUpdateClient();
  const loading = createMutation.isPending || updateMutation.isPending;
  const [form, setForm] = useState<CreateClientInput>({
    name: "",
    surname: "",
    email: "",
    doc_type: "DNI",
    doc_number: "",
    phone: "",
    address: "",
    city: "",
  });

  useEffect(() => {
    if (client) {
      setForm({
        name: client.name,
        surname: client.surname,
        email: client.email,
        doc_type: client.doc_type || "DNI",
        doc_number: client.doc_number || "",
        phone: client.phone || "",
        address: client.address || "",
        city: client.city || "",
      });
    } else {
      setForm({
        name: "",
        surname: "",
        email: "",
        doc_type: "DNI",
        doc_number: "",
        phone: "",
        address: "",
        city: "",
      });
    }
  }, [client, open]);

  async function handleSubmit() {
    try {
      if (client) {
        await updateMutation.mutateAsync({ id: client.id, data: form });
      } else {
        await createMutation.mutateAsync(form);
      }
      onClose();
    } catch {
      alert("Error al guardar el cliente");
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={client ? "Editar cliente" : "Nuevo cliente"}
    >
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <Input
            label="Nombre"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
          <Input
            label="Apellido"
            value={form.surname}
            onChange={(e) => setForm({ ...form, surname: e.target.value })}
          />
        </div>
        <Input
          label="Email"
          type="email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <div className="grid grid-cols-2 gap-3">
          <Input
            label="Tipo documento"
            value={form.doc_type}
            onChange={(e) => setForm({ ...form, doc_type: e.target.value })}
          />
          <Input
            label="Número"
            value={form.doc_number}
            onChange={(e) => setForm({ ...form, doc_number: e.target.value })}
          />
        </div>
        <Input
          label="Teléfono"
          value={form.phone}
          onChange={(e) => setForm({ ...form, phone: e.target.value })}
        />
        <Input
          label="Dirección"
          value={form.address}
          onChange={(e) => setForm({ ...form, address: e.target.value })}
        />
        <Input
          label="Ciudad"
          value={form.city}
          onChange={(e) => setForm({ ...form, city: e.target.value })}
        />
        <div className="flex gap-3 pt-2">
          <Button variant="ghost" onClick={onClose} className="flex-1">
            Cancelar
          </Button>
          <Button
            className="flex-1"
            loading={loading}
            onClick={handleSubmit}
            disabled={!form.name || !form.surname || !form.email}
          >
            {client ? "Guardar cambios" : "Crear cliente"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
