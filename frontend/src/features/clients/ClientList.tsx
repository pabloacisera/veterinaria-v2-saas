import { useState } from "react";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { Table, type Column } from "@/shared/ui/Table";
import { Pagination } from "@/shared/ui/Pagination";
import { useClients, useDeleteClient } from "@/shared/hooks/useClients";
import type { ClientData } from "./api";

const PAGE_SIZE = 20;

interface ClientListProps {
  onEdit: (client: ClientData) => void;
  onCreate: () => void;
}

export function ClientList({ onEdit, onCreate }: ClientListProps) {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const { data, isLoading } = useClients({ search: search || undefined, limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE });
  const clients = data?.items ?? [];
  const totalCount = data?.total_count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));
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
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
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
      <Pagination page={page} totalPages={totalPages} totalItems={totalCount} onPageChange={setPage} />
    </div>
  );
}
