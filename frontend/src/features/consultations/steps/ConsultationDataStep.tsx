import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import type { ClientData } from "@/entities/client/types";
import type { PetData } from "@/entities/pet/types";

interface ConsultationDataStepProps {
  selectedPet: PetData | null;
  selectedClient: ClientData | null;
  reason: string;
  onReasonChange: (value: string) => void;
  diagnosis: string;
  onDiagnosisChange: (value: string) => void;
  treatment: string;
  onTreatmentChange: (value: string) => void;
  onBack: () => void;
  onNext: () => void;
}

export function ConsultationDataStep({
  selectedPet,
  selectedClient,
  reason,
  onReasonChange,
  diagnosis,
  onDiagnosisChange,
  treatment,
  onTreatmentChange,
  onBack,
  onNext,
}: ConsultationDataStepProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Datos de la consulta</h2>
      <p className="text-sm text-gray-500">
        Paciente: <span className="font-medium text-gray-900">{selectedPet?.name}</span>
        {selectedClient && (
          <> (dueño: {selectedClient.name} {selectedClient.surname})</>
        )}
      </p>

      <Input
        label="Motivo de consulta"
        value={reason}
        onChange={(e) => onReasonChange(e.target.value)}
      />
      <Input
        label="Diagnóstico"
        value={diagnosis}
        onChange={(e) => onDiagnosisChange(e.target.value)}
      />
      <Input
        label="Tratamiento (opcional)"
        value={treatment}
        onChange={(e) => onTreatmentChange(e.target.value)}
      />

      <div className="flex gap-3 pt-2">
        <Button variant="ghost" onClick={onBack}>Atrás</Button>
        <div className="flex-1" />
        <Button
          onClick={onNext}
          disabled={!reason || !diagnosis}
        >
          Continuar
        </Button>
      </div>
    </div>
  );
}
