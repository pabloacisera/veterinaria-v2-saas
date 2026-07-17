import { Card } from "@/shared/ui/Card";
import { Button } from "@/shared/ui/Button";
import type { Prescripcion } from "@/entities/client-portal";

interface Props {
  prescripciones: Prescripcion[];
  loading: boolean;
}

export function ClientePrescripciones({ prescripciones, loading }: Props) {
  if (loading) {
    return <p className="text-gray-500">Cargando prescripciones...</p>;
  }

  if (prescripciones.length === 0) {
    return <p className="text-gray-500">No hay prescripciones disponibles.</p>;
  }

  return (
    <div className="space-y-3">
      {prescripciones.map((p) => (
        <Card key={p.id} className="p-4 flex items-center justify-between">
          <div>
            <p className="font-medium text-gray-900">Prescripción #{p.version}</p>
            <p className="text-sm text-gray-500">{new Date(p.created_at).toLocaleDateString()}</p>
          </div>
          {p.download_url && (
            <Button variant="outline" size="sm" onClick={() => window.open(p.download_url!, "_blank")}>
              Descargar
            </Button>
          )}
        </Card>
      ))}
    </div>
  );
}
