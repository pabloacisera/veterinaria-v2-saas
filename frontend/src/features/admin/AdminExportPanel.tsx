import { useState } from "react";
import { Button } from "@/shared/ui/Button";
import { Card } from "@/shared/ui/Card";
import { exportCompanias } from "./api";

export function AdminExportPanel() {
  const [exporting, setExporting] = useState(false);
  const [message, setMessage] = useState("");

  async function handleExport() {
    setExporting(true);
    setMessage("");
    try {
      await exportCompanias();
      setMessage("Exportación completada exitosamente");
    } catch (err) {
      setMessage(
        err instanceof Error ? err.message : "Error al exportar"
      );
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">
          Exportar Datos
        </h2>
        <p className="text-sm text-gray-500">
          Exportar información del sistema a formato CSV
        </p>
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

      <Card>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900">Compañías</h3>
            <p className="text-sm text-gray-500">
              Exportar lista completa de compañías con datos de suscripción
            </p>
          </div>
          <Button onClick={handleExport} loading={exporting}>
            Exportar CSV
          </Button>
        </div>
      </Card>
    </div>
  );
}
