import { useState, useRef } from "react";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { Table, type Column } from "@/shared/ui/Table";
import { Badge } from "@/shared/ui/Badge";
import { useSupplies, useDeleteSupply } from "@/shared/hooks/useSupplies";
import { uploadSuppliesCsv, downloadTemplate } from "./api";
import type { SupplyData } from "./api";

interface SupplyListProps {
  onEdit: (supply: SupplyData) => void;
  onCreate: () => void;
}

export function SupplyList({ onEdit, onCreate }: SupplyListProps) {
  const [search, setSearch] = useState("");
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { data: supplies = [], isLoading, refetch } = useSupplies({ search: search || undefined, limit: 100 });
  const deleteMutation = useDeleteSupply();

  async function handleDelete(id: string) {
    if (!confirm("¿Eliminar este insumo?")) return;
    try {
      await deleteMutation.mutateAsync(id);
    } catch {
      alert("Error al eliminar el insumo");
    }
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const result = await uploadSuppliesCsv(file);
      if (result.errors.length > 0) {
        const msg = result.errors.map((er) => `Fila ${er.fila}: ${er.error}`).join("\n");
        alert(`${result.created} creados. Errores:\n${msg}`);
      } else {
        alert(`${result.created} insumos creados correctamente`);
      }
      refetch();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error al subir archivo";
      alert(message);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
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
        <div className="flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx"
            className="hidden"
            onChange={handleUpload}
          />
          <Button
            variant="ghost"
            onClick={downloadTemplate}
          >
            Descargar plantilla
          </Button>
          <Button
            variant="ghost"
            loading={uploading}
            onClick={() => fileInputRef.current?.click()}
          >
            Subir CSV
          </Button>
          <Button onClick={onCreate}>Nuevo insumo</Button>
        </div>
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
