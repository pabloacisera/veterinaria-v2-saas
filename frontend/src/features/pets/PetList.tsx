import { useState } from "react";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { Table, type Column } from "@/shared/ui/Table";
import { Pagination } from "@/shared/ui/Pagination";
import { usePets, useDeletePet } from "@/shared/hooks/usePets";
import type { PetData } from "./api";

const PAGE_SIZE = 20;

interface PetListProps {
  onEdit: (pet: PetData) => void;
  onCreate: () => void;
  ownerId?: string;
}

export function PetList({ onEdit, onCreate, ownerId }: PetListProps) {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const { data, isLoading } = usePets({ search: search || undefined, owner_id: ownerId, limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE });
  const pets = data?.items ?? [];
  const totalCount = data?.total_count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));
  const deleteMutation = useDeletePet();

  async function handleDelete(id: string) {
    if (!confirm("¿Eliminar esta mascota?")) return;
    try {
      await deleteMutation.mutateAsync(id);
    } catch {
      alert("Error al eliminar la mascota");
    }
  }

  const columns: Column<PetData>[] = [
    { header: "Nombre", render: (p) => p.name || "-" },
    { header: "Especie", render: (p) => p.species || "-" },
    { header: "Raza", render: (p) => p.breed || "-" },
    { header: "Sexo", accessor: "sex" },
    {
      header: "Peso",
      render: (p) => (p.weight_kg ? `${p.weight_kg} kg` : "-"),
    },
    { header: "Color", render: (p) => p.color || "-" },
    {
      header: "Acciones",
      className: "text-right",
      render: (p) => (
        <div className="flex gap-2 justify-end">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onEdit(p);
            }}
          >
            Editar
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              handleDelete(p.id);
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
            placeholder="Buscar mascota..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        <Button onClick={onCreate}>Nueva mascota</Button>
      </div>
      <Table
        columns={columns}
        data={pets}
        keyExtractor={(p) => p.id}
        loading={isLoading}
        emptyMessage="No hay mascotas registradas"
      />
      <Pagination page={page} totalPages={totalPages} totalItems={totalCount} onPageChange={setPage} />
    </div>
  );
}
