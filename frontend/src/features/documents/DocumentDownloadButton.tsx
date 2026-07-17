import { useState, useCallback } from "react";
import { Button } from "@/shared/ui/Button";
import { apiGetBlob } from "@/shared/lib/api";

interface DocumentDownloadButtonProps {
  entityId: string;
  entityType: "consulta" | "venta";
  documentType: "factura" | "prescripcion";
  filename?: string;
}

export function DocumentDownloadButton({
  entityId,
  entityType,
  documentType,
  filename,
}: DocumentDownloadButtonProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleDownload = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const blob = await apiGetBlob(
        `/${entityType}/${entityId}/${documentType}/download`
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename || `${documentType}_${entityId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error al descargar";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [entityId, entityType, documentType, filename]);

  return (
    <div className="inline-flex flex-col items-start gap-1">
      <Button
        variant="outline"
        size="sm"
        onClick={handleDownload}
        loading={loading}
      >
        {documentType === "factura" ? "Descargar factura" : "Descargar prescripción"}
      </Button>
      {error && (
        <div className="flex items-center gap-2">
          <p className="text-sm text-red-600">{error}</p>
          <button
            type="button"
            onClick={handleDownload}
            className="text-xs text-primary-600 hover:text-primary-700 underline"
          >
            Reintentar
          </button>
        </div>
      )}
    </div>
  );
}
