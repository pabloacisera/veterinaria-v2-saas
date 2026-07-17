import { useState } from "react";
import { Table, type Column } from "@/shared/ui/Table";
import { Badge } from "@/shared/ui/Badge";
import { Button } from "@/shared/ui/Button";
import { Input } from "@/shared/ui/Input";
import { useCompanias, useBlockCompania, useUnblockCompania } from "@/shared/hooks/useAdmin";
import type { CompanyAdmin } from "./api";

const statusBadge: Record<string, "success" | "warning" | "danger" | "default"> = {
  activa: "success",
  trial: "default",
  vencida: "warning",
  bloqueada: "danger",
};

interface AdminCompanyListProps {
  onSelect: (company: CompanyAdmin) => void;
}

export function AdminCompanyList({ onSelect }: AdminCompanyListProps) {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [estado, setEstado] = useState("");
  const [plan, setPlan] = useState("");

  const { data, isLoading } = useCompanias(page, 20);
  const blockMutation = useBlockCompania();
  const unblockMutation = useUnblockCompania();

  const companies = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.ceil(total / 20);
  const actionLoading = blockMutation.isPending || unblockMutation.isPending;

  async function handleBlock(company: CompanyAdmin) {
    try {
      if (company.estado === "bloqueada") {
        await unblockMutation.mutateAsync(company.id);
      } else {
        await blockMutation.mutateAsync(company.id);
      }
    } catch {
      // ignore
    }
  }

  const columns: Column<CompanyAdmin>[] = [
    { header: "CUIT", accessor: "cuit" },
    { header: "Nombre", accessor: "nombre" },
    {
      header: "Plan",
      render: (row) => (row.plan ? row.plan : "—"),
    },
    {
      header: "Estado",
      render: (row) => (
        <Badge variant={statusBadge[row.estado ?? ""] ?? "default"}>
          {row.estado ?? "—"}
        </Badge>
      ),
    },
    {
      header: "Inicio Susc.",
      render: (row) =>
        row.inicio_suscripcion
          ? new Date(row.inicio_suscripcion).toLocaleDateString()
          : "—",
    },
    {
      header: "Fin Susc.",
      render: (row) =>
        row.fin_suscripcion
          ? new Date(row.fin_suscripcion).toLocaleDateString()
          : "—",
    },
    {
      header: "Acciones",
      render: (row) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={(e) => {
              e.stopPropagation();
              onSelect(row);
            }}
          >
            Detalle
          </Button>
          <Button
            size="sm"
            variant={row.estado === "bloqueada" ? "secondary" : "outline"}
            loading={actionLoading}
            onClick={(e) => {
              e.stopPropagation();
              handleBlock(row);
            }}
          >
            {row.estado === "bloqueada" ? "Desbloquear" : "Bloquear"}
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[200px]">
          <Input
            label="Buscar"
            placeholder="CUIT o nombre..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Estado
          </label>
          <select
            value={estado}
            onChange={(e) => {
              setEstado(e.target.value);
              setPage(1);
            }}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">Todos</option>
            <option value="activa">Activa</option>
            <option value="vencida">Vencida</option>
            <option value="bloqueada">Bloqueada</option>
            <option value="trial">Trial</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Plan
          </label>
          <select
            value={plan}
            onChange={(e) => {
              setPlan(e.target.value);
              setPage(1);
            }}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">Todos</option>
            <option value="mensual">Mensual</option>
            <option value="semestral">Semestral</option>
            <option value="anual">Anual</option>
          </select>
        </div>
      </div>

      <Table
        columns={columns}
        data={companies}
        keyExtractor={(r) => r.id}
        loading={isLoading}
        emptyMessage="No se encontraron compañías"
      />

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Página {page} de {totalPages} ({total} registros)
          </p>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Anterior
            </Button>
            <Button
              variant="secondary"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Siguiente
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
