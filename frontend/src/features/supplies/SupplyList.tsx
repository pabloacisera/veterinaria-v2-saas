import { useState } from "react";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { Table, type Column } from "@/shared/ui/Table";
import { Badge } from "@/shared/ui/Badge";
import { useSupplies, useDeleteSupply } from "@/shared/hooks/useSupplies";
import type { SupplyData } from "./api";

interface SupplyListProps {
  onEdit: (supply: SupplyData) => void;
  onCreate: () => void;
}

export function SupplyList({ onEdit, onCreate }: SupplyListProps) {
  const [search, setSearch] = useState("");
  const { data: supplies = [], isLoading } = useSupplies({ search: search || undefined, limit: 100 });
  const deleteMutation = useDeleteSupply();

  async function handleDelete(id: string) {
    if (!confirm("¿Eliminar este insumo?")) return;
    try {
      await deleteMutation.mutateAsync(id);
    } catch {
      alert("Error al eliminar el insumo");
    }
  }

  const columns: Column<SupplyData>[] = [
    { header: "Nombre", accessor: "name" },
    { header: "Marca", render: (s) => s.brand || "-" },
    { header: "Unidad", accessor: "unit_base" },
    {
      header: "Precio",
      render: (s) => `$${Number(s.unit_price).toLocaleString("es-AR")}`,
    },
    {
      header: "Stock",
      render: (s) => {
        const stock = Number(s.stock_quantity);
        const min = Number(s.min_stock);
        const isLow = min > 0 && stock <= min;
        return (
          <Badge variant={isLow ? "danger" : stock > 0 ? "success" : "warning"}>
            {stock} {s.unit_base}
          </Badge>
        );
      },
    },
    {
      header: "Stock mín.",
      render: (s) => (Number(s.min_stock) > 0 ? `${Number(s.min_stock)} ${s.unit_base}` : "-"),
    },
    {
      header: "Acciones",
      className: "text-right",
      render: (s) => (
        <div className="flex gap-2 justify-end">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onEdit(s);
            }}
          >
            Editar
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              handleDelete(s.id);
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
            placeholder="Buscar insumo..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Button onClick={onCreate}>Nuevo insumo</Button>
      </div>
      <Table
        columns={columns}
        data={supplies}
        keyExtractor={(s) => s.id}
        loading={isLoading}
        emptyMessage="No hay insumos registrados"
      />
    </div>
  );
}
