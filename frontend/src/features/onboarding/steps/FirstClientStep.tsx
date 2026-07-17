import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";

interface ClientFormData {
  name: string;
  surname: string;
  email: string;
  doc_type: string;
  doc_number: string;
  phone: string;
}

interface FirstClientStepProps {
  clientData: ClientFormData;
  onClientDataChange: (data: ClientFormData) => void;
  loading: boolean;
  onSave: () => void;
  onSkip: () => void;
}

export function FirstClientStep({
  clientData,
  onClientDataChange,
  loading,
  onSave,
  onSkip,
}: FirstClientStepProps) {
  const set = (field: keyof ClientFormData) => (e: React.ChangeEvent<HTMLInputElement>) =>
    onClientDataChange({ ...clientData, [field]: e.target.value });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Registrá tu primer cliente</h2>
      <p className="text-sm text-gray-500">
        Estos datos son necesarios para empezar a operar. Después podrás agregar más clientes.
      </p>
      <div className="grid grid-cols-2 gap-3">
        <Input label="Nombre" value={clientData.name} onChange={set("name")} />
        <Input label="Apellido" value={clientData.surname} onChange={set("surname")} />
      </div>
      <Input label="Email" type="email" value={clientData.email} onChange={set("email")} />
      <div className="grid grid-cols-2 gap-3">
        <Input label="Tipo Doc." value={clientData.doc_type} onChange={set("doc_type")} />
        <Input label="Número" value={clientData.doc_number} onChange={set("doc_number")} />
      </div>
      <Input label="Teléfono" value={clientData.phone} onChange={set("phone")} />
      <div className="flex gap-3 pt-2">
        <Button variant="ghost" onClick={onSkip}>Saltar</Button>
        <Button
          className="flex-1"
          loading={loading}
          onClick={onSave}
          disabled={!clientData.name || !clientData.surname || !clientData.email}
        >
          Guardar cliente
        </Button>
      </div>
    </div>
  );
}
