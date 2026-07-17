import { useState } from "react";
import { Button } from "@/shared/ui/Button";
import { Table, type Column } from "@/shared/ui/Table";
import { Badge } from "@/shared/ui/Badge";
import { useBackupHistorial, useTriggerBackup } from "@/shared/hooks/useAdmin";
import type { BackupLogItem } from "./api";

const statusBadge: Record<string, "success" | "danger" | "warning"> = {
  ok: "success",
  error: "danger",
  en_proceso: "warning",
};

export function AdminBackupPanel() {
  const { data: backups = [], isLoading } = useBackupHistorial();
  const triggerMutation = useTriggerBackup();
  const [message, setMessage] = useState("");

  async function handleManualBackup() {
    setMessage("");
    try {
      const res = await triggerMutation.mutateAsync();
      setMessage(res.status === "backup_encolado" ? "Backup encolado exitosamente" : "Error al encolar backup");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Error al generar backup");
    }
  }

  const columns: Column<BackupLogItem>[] = [
    { header: "Tipo", accessor: "tipo" },
    {
      header: "Estado",
      render: (row) => (
        <Badge variant={statusBadge[row.estado] ?? "default"}>
          {row.estado}
        </Badge>
      ),
    },
    { header: "Mensaje", accessor: "mensaje" },
    {
      header: "Ejecutado",
      render: (row) => new Date(row.ejecutado_en).toLocaleString(),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            Backup de Base de Datos
          </h2>
          <p className="text-sm text-gray-500">
            Generar y visualizar backups del sistema
          </p>
        </div>
        <Button onClick={handleManualBackup} loading={triggerMutation.isPending}>
          Generar Backup Manual
        </Button>
      </div>

      {message && (
        <div
          className={`p-3 rounded-lg text-sm ${
            message.includes("Error") || message.includes("error")
              ? "bg-red-50 text-red-700 border border-red-200"
              : "bg-green-50 text-green-700 border border-green-200"
          }`}
        >
          {message}
        </div>
      )}

      <Table
        columns={columns}
        data={backups}
        keyExtractor={(r) => r.id}
        loading={isLoading}
        emptyMessage="No hay registros de backup"
      />
    </div>
  );
}
