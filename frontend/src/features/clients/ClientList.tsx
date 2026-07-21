import { useState } from "react";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { Table, type Column } from "@/shared/ui/Table";
import { useClients, useDeleteClient } from "@/shared/hooks/useClients";
import type { ClientData } from "./api";

interface ClientListProps {
  onEdit: (client: ClientData) => void;
  onCreate: () => void;
}

export function ClientList({ onEdit, onCreate }: ClientListProps) {
  const [search, setSearch] = useState("");
  const { data: clients = [], isLoading } = useClients({ search: search || undefined, limit: 100 });
  const deleteMutation = useDeleteClient();

  async function handleDelete(id: string) {
    if (!confirm("¿Eliminar este cliente?")) return;
    try {
      await deleteMutation.mutateAsync(id);
    } catch {
      alert("Error al eliminar el cliente");
    }
  }

  const columns: Column<ClientData>[] = [
    { header: "Nombre", render: (c) => `${c.name} ${c.surname}` },
    { header: "Email", accessor: "email" },
    {
      header: "Documento",
      render: (c) =>
        c.doc_type && c.doc_number
          ? `${c.doc_type} ${c.doc_number}`
          : "-",
    },
    { header: "Teléfono", render: (c) => c.phone || "-" },
    {
      header: "Acciones",
      className: "text-right",
      render: (c) => (
        <div className="flex gap-2 justify-end">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onEdit(c);
            }}
          >
            Editar
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              handleDelete(c.id);
            }}
          >
            Eliminar
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="flex-1 max-w-sm">
          <Input
            placeholder="Buscar cliente..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Button onClick={onCreate}>Nuevo cliente</Button>
      </div>
      <Table
        columns={columns}
        data={clients}
        keyExtractor={(c) => c.id}
        loading={isLoading}
        emptyMessage="No hay clientes registrados"
      />
    </div>
  );
}
