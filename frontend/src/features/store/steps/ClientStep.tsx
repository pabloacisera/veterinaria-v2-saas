import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import type { ClientData } from "@/entities/client/types";

interface ClientStepProps {
  clientSearch: string;
  onClientSearchChange: (value: string) => void;
  filteredClients: ClientData[];
  selectedClient: ClientData | null;
  onSelectClient: (client: ClientData) => void;
  clientName: string;
  onClientNameChange: (value: string) => void;
  onCancel: () => void;
  onNext: () => void;
}

export function ClientStep({
  clientSearch,
  onClientSearchChange,
  filteredClients,
  selectedClient,
  onSelectClient,
  clientName,
  onClientNameChange,
  onCancel,
  onNext,
}: ClientStepProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Cliente</h2>
      <p className="text-sm text-gray-500">
        Buscá un cliente existente o completá el nombre para una venta al público.
      </p>

      <div>
        <Input
          label="Buscar cliente"
          value={clientSearch}
          onChange={(e) => onClientSearchChange(e.target.value)}
          placeholder="Nombre, apellido o email..."
        />
        {clientSearch && !selectedClient && filteredClients.length > 0 && (
          <div className="mt-1 border border-gray-200 rounded-lg max-h-48 overflow-y-auto">
            {filteredClients.slice(0, 10).map((c) => (
              <button
                key={c.id}
                type="button"
                className="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm border-b border-gray-50 last:border-0"
                onClick={() => onSelectClient(c)}
              >
                <span className="font-medium">{c.name} {c.surname}</span>
                {c.email && <span className="text-gray-400 ml-2">({c.email})</span>}
              </button>
            ))}
          </div>
        )}
      </div>

      {selectedClient && (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-3 text-sm">
          <span className="font-medium text-primary-800">
            {selectedClient.name} {selectedClient.surname}
          </span>
          {selectedClient.doc_type && selectedClient.doc_number && (
            <span className="text-primary-600 ml-2">
              {selectedClient.doc_type}: {selectedClient.doc_number}
            </span>
          )}
          <p className="text-primary-600 text-xs mt-1">Cliente seleccionado</p>
        </div>
      )}

      {!selectedClient && (
        <Input
          label="Nombre del cliente (opcional)"
          value={clientName}
          onChange={(e) => onClientNameChange(e.target.value)}
          placeholder="Venta al público"
        />
      )}

      <div className="flex gap-3 pt-2">
        <Button variant="ghost" onClick={onCancel}>Cancelar</Button>
        <div className="flex-1" />
        <Button onClick={onNext}>Continuar</Button>
      </div>
    </div>
  );
}
