import { useState } from "react";
import { Button } from "@/shared/ui/Button";
import { Table, type Column } from "@/shared/ui/Table";
import { Badge } from "@/shared/ui/Badge";
import { useMovements, useUpdateMovementStatus } from "@/shared/hooks/useCash";
import type { CashMovementData } from "./api";

interface CashMovementListProps {
  onCreate: () => void;
}

const typeLabels: Record<string, string> = {
  income: "Ingreso",
  expense: "Egreso",
};

export function CashMovementList({ onCreate }: CashMovementListProps) {
  const [filterType, setFilterType] = useState<string>("");
  const [filterStatus, setFilterStatus] = useState<string>("");
  const { data: movements = [], isLoading } = useMovements({
    movement_type: filterType || undefined,
    status: filterStatus || undefined,
    limit: 100,
  });
  const updateStatusMutation = useUpdateMovementStatus();

  async function handleToggleStatus(m: CashMovementData) {
    const newStatus = m.status === "pagado" ? "pendiente" : "pagado";
    try {
      await updateStatusMutation.mutateAsync({ id: m.id, status: newStatus });
    } catch {
      alert("Error al actualizar el estado");
    }
  }

  const totalIncome = movements
    .filter((m) => m.movement_type === "income")
    .reduce((sum, m) => sum + Number(m.amount), 0);

  const totalExpense = movements
    .filter((m) => m.movement_type === "expense")
    .reduce((sum, m) => sum + Number(m.amount), 0);

  const columns: Column<CashMovementData>[] = [
    {
      header: "Tipo",
      render: (m) => (
        <Badge variant={m.movement_type === "income" ? "success" : "danger"}>
          {typeLabels[m.movement_type] || m.movement_type}
        </Badge>
      ),
    },
    { header: "Categoría", render: (m) => m.category || "-" },
    {
      header: "Monto",
      render: (m) => (
        <span
          className={
            m.movement_type === "income" ? "text-green-600" : "text-red-600"
          }
        >
          ${Number(m.amount).toLocaleString("es-AR")}
        </span>
      ),
    },
    { header: "Descripción", render: (m) => m.description || "-" },
    { header: "Método pago", render: (m) => m.payment_method || "-" },
    {
      header: "Estado",
      render: (m) => (
        <Badge variant={m.status === "pagado" ? "success" : "warning"}>
          {m.status === "pagado" ? "Pagado" : "Pendiente"}
        </Badge>
      ),
    },
    {
      header: "Fecha",
      render: (m) =>
        new Date(m.created_at).toLocaleDateString("es-AR", {
          day: "2-digit",
          month: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        }),
    },
    {
      header: "Acciones",
      className: "text-right",
      render: (m) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            handleToggleStatus(m);
          }}
        >
          {m.status === "pagado" ? "Marcar pendiente" : "Marcar pagado"}
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      {/* Resumen */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-green-50 rounded-xl p-4">
          <p className="text-sm text-green-700 font-medium">Ingresos</p>
          <p className="text-2xl font-bold text-green-700">
            ${totalIncome.toLocaleString("es-AR")}
          </p>
        </div>
        <div className="bg-red-50 rounded-xl p-4">
          <p className="text-sm text-red-700 font-medium">Egresos</p>
          <p className="text-2xl font-bold text-red-700">
            ${totalExpense.toLocaleString("es-AR")}
          </p>
        </div>
        <div className="bg-blue-50 rounded-xl p-4">
          <p className="text-sm text-blue-700 font-medium">Balance</p>
          <p className="text-2xl font-bold text-blue-700">
            ${(totalIncome - totalExpense).toLocaleString("es-AR")}
          </p>
        </div>
      </div>

      {/* Filtros */}
      <div className="flex items-center gap-3">
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">Todos los tipos</option>
          <option value="income">Ingresos</option>
          <option value="expense">Egresos</option>
        </select>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">Todos los estados</option>
          <option value="pagado">Pagados</option>
          <option value="pendiente">Pendientes</option>
        </select>
        <div className="flex-1" />
        <Button onClick={onCreate}>Nuevo movimiento</Button>
      </div>

      <Table
        columns={columns}
        data={movements}
        keyExtractor={(m) => m.id}
        loading={isLoading}
        emptyMessage="No hay movimientos registrados"
      />
    </div>
  );
}
