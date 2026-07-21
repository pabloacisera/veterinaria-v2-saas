import { useMemo, useState } from "react";
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
}

export function PetList({ onEdit, onCreate }: PetListProps) {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const offset = (page - 1) * PAGE_SIZE;
  const { data: pets = [], total, isLoading } = usePets({
    search: search || undefined,
    limit: PAGE_SIZE,
    offset,
  });
  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / PAGE_SIZE)), [total]);
  const deleteMutation = useDeletePet();

  function handleSearch(value: string) {
    setSearch(value);
    setPage(1);
  }

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
            onChange={(e) => handleSearch(e.target.value)}
          />
        </div>
        <Button onClick={onCreate}>Nueva mascota</Button>
      </div>
      <div className="rounded-lg border border-gray-100">
        <Table
          columns={columns}
          data={pets}
          keyExtractor={(p) => p.id}
          loading={isLoading}
          emptyMessage="No hay mascotas registradas"
        />
        <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
      </div>
    </div>
  );
}
