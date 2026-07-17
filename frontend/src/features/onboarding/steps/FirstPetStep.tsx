import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";

interface PetFormData {
  name: string;
  species: string;
  breed: string;
  sex: string;
  color: string;
  birth_date: string;
}

interface FirstPetStepProps {
  petData: PetFormData;
  onPetDataChange: (data: PetFormData) => void;
  loading: boolean;
  onSave: () => void;
  onSkip: () => void;
}

export function FirstPetStep({
  petData,
  onPetDataChange,
  loading,
  onSave,
  onSkip,
}: FirstPetStepProps) {
  const set = (field: keyof PetFormData) => (e: React.ChangeEvent<HTMLInputElement>) =>
    onPetDataChange({ ...petData, [field]: e.target.value });

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Registrá la primera mascota</h2>
      <p className="text-sm text-gray-500">Agregá la primera mascota para tu cliente.</p>
      <div className="grid grid-cols-2 gap-3">
        <Input label="Nombre" value={petData.name} onChange={set("name")} />
        <Input label="Especie" value={petData.species} onChange={set("species")} />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <Input label="Raza" value={petData.breed} onChange={set("breed")} />
        <Input label="Sexo" value={petData.sex} onChange={set("sex")} />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <Input label="Color" value={petData.color} onChange={set("color")} />
        <Input label="Fecha nac." type="date" value={petData.birth_date} onChange={set("birth_date")} />
      </div>
      <div className="flex gap-3 pt-2">
        <Button variant="ghost" onClick={onSkip}>Saltar</Button>
        <Button
          className="flex-1"
          loading={loading}
          onClick={onSave}
          disabled={!petData.name}
        >
          Guardar mascota
        </Button>
      </div>
    </div>
  );
}
