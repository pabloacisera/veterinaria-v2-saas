import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";

interface ClientStepProps {
  clientName: string;
  onClientNameChange: (value: string) => void;
  onCancel: () => void;
  onNext: () => void;
}

export function ClientStep({ clientName, onClientNameChange, onCancel, onNext }: ClientStepProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Cliente</h2>
      <p className="text-sm text-gray-500">
        Opcional: ingresá el nombre del cliente o continuá como venta al público.
      </p>
      <Input
        label="Nombre del cliente"
        value={clientName}
        onChange={(e) => onClientNameChange(e.target.value)}
        placeholder="Venta al público"
      />
      <div className="flex gap-3 pt-2">
        <Button variant="ghost" onClick={onCancel}>Cancelar</Button>
        <div className="flex-1" />
        <Button onClick={onNext}>Continuar</Button>
      </div>
    </div>
  );
}
