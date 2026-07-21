import { useState } from "react";
import { ClientList } from "@/features/clients/ClientList";
import { ClientForm } from "@/features/clients/ClientForm";
import type { ClientData } from "@/entities/client/types";

export function DashboardClients() {
  const [formOpen, setFormOpen] = useState(false);
  const [editingClient, setEditingClient] = useState<ClientData | null>(null);

  function handleEdit(client: ClientData) {
    setEditingClient(client);
    setFormOpen(true);
  }

  function handleCreate() {
    setEditingClient(null);
    setFormOpen(true);
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Clientes</h1>
      <ClientList onEdit={handleEdit} onCreate={handleCreate} />
      <ClientForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        client={editingClient}
      />
    </div>
  );
}

export default DashboardClients;
