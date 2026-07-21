import { useState } from "react";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { Table, type Column } from "@/shared/ui/Table";
import { Badge } from "@/shared/ui/Badge";
import { Pagination } from "@/shared/ui/Pagination";
import { ConsultationWizard } from "@/features/consultations/ConsultationWizard";
import { useConsultations } from "@/shared/hooks/useConsultations";
import {
  downloadFactura, downloadPrescripcion,
  type ConsultationData,
} from "@/features/consultations/api";

const PAGE_SIZE = 20;

const statusLabels: Record<string, string> = {
  draft: "Borrador",
  completed: "Completada",
  cancelled: "Cancelada",
};

export function DashboardConsultas() {
  const [showWizard, setShowWizard] = useState(false);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const { data, isLoading } = useConsultations({ search: search || undefined, limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE });
  const consultations = data?.items ?? [];
  const totalCount = data?.total_count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  if (showWizard) {
    return (
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          Nueva consulta
        </h1>
        <ConsultationWizard
          onComplete={() => setShowWizard(false)}
          onCancel={() => setShowWizard(false)}
        />
      </div>
    );
  }

  const columns: Column<ConsultationData>[] = [
    { header: "Motivo", accessor: "reason" },
    { header: "Diagnóstico", render: (c) => c.diagnosis || "-" },
    {
      header: "Estado",
      render: (c) => (
        <Badge
          variant={
            c.status === "completed"
              ? "success"
              : c.status === "draft"
                ? "warning"
                : "default"
          }
        >
          {statusLabels[c.status] || c.status}
        </Badge>
      ),
    },
    {
      header: "Fecha",
      render: (c) =>
        new Date(c.created_at).toLocaleDateString("es-AR", {
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        }),
    },
    {
      header: "Acciones",
      render: (c) => (
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={async (e) => {
              e.stopPropagation();
              const res = await downloadFactura(c.id);
              if (res.download_url) window.open(res.download_url, "_blank");
            }}
          >
            Factura
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={async (e) => {
              e.stopPropagation();
              const res = await downloadPrescripcion(c.id);
              if (res.download_url) window.open(res.download_url, "_blank");
            }}
          >
            Receta
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Consultas</h1>
        <Button onClick={() => setShowWizard(true)}>Nueva consulta</Button>
      </div>
      <div className="mb-4 max-w-sm">
        <Input
          placeholder="Buscar consulta..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
      </div>
      <Table
        columns={columns}
        data={consultations}
        keyExtractor={(c) => c.id}
        loading={isLoading}
        emptyMessage="No hay consultas registradas"
      />
      <Pagination page={page} totalPages={totalPages} totalItems={totalCount} onPageChange={setPage} />
    </div>
  );
}

export default DashboardConsultas;
