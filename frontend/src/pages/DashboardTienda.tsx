import { useState } from "react";
import { Button } from "@/shared/ui/Button";
import { Table, type Column } from "@/shared/ui/Table";
import { Badge } from "@/shared/ui/Badge";
import { SaleWizard } from "@/features/store/SaleWizard";
import { useSales } from "@/shared/hooks/useStore";
import { downloadSaleFactura } from "@/features/store/api";
import type { SaleData } from "@/entities/store/types";

export function DashboardTienda() {
  const [showWizard, setShowWizard] = useState(false);
  const { data: sales = [], isLoading } = useSales({ limit: 50 });

  if (showWizard) {
    return (
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          Nueva venta
        </h1>
        <SaleWizard
          onComplete={() => setShowWizard(false)}
          onCancel={() => setShowWizard(false)}
        />
      </div>
    );
  }

  const columns: Column<SaleData>[] = [
    {
      header: "Cliente",
      render: (s) => s.client_name || "Venta al público",
    },
    {
      header: "Monto",
      render: (s) => `$${Number(s.total).toLocaleString("es-AR")}`,
    },
    {
      header: "Método pago",
      render: (s) => (
        <span className="capitalize">{s.payment_method}</span>
      ),
    },
    {
      header: "Estado",
      render: (s) => (
        <Badge variant={s.status === "completed" ? "success" : "warning"}>
          {s.status === "completed" ? "Completada" : s.status}
        </Badge>
      ),
    },
    {
      header: "Fecha",
      render: (s) =>
        new Date(s.created_at).toLocaleDateString("es-AR", {
          day: "2-digit",
          month: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        }),
    },
    {
      header: "Acciones",
      render: (s) => (
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={async (e) => {
              e.stopPropagation();
              const res = await downloadSaleFactura(s.id);
              if (res.download_url) window.open(res.download_url, "_blank");
            }}
          >
            Factura
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Tienda</h1>
        <Button onClick={() => setShowWizard(true)}>Nueva venta</Button>
      </div>
      <Table
        columns={columns}
        data={sales}
        keyExtractor={(s) => s.id}
        loading={isLoading}
        emptyMessage="No hay ventas registradas"
      />
    </div>
  );
}

export default DashboardTienda;
