import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import type { ClientData } from "@/entities/client/types";
import type { PetData } from "@/entities/pet/types";

interface PetSelectionStepProps {
  clientSearch: string;
  onClientSearchChange: (value: string) => void;
  filteredClients: ClientData[];
  selectedClient: ClientData | null;
  onSelectClient: (client: ClientData) => void;
  petSearch: string;
  onPetSearchChange: (value: string) => void;
  filteredPets: PetData[];
  selectedPet: PetData | null;
  onSelectPet: (pet: PetData) => void;
  onCancel: () => void;
  onNext: () => void;
}

export function PetSelectionStep({
  clientSearch,
  onClientSearchChange,
  filteredClients,
  selectedClient,
  onSelectClient,
  petSearch,
  onPetSearchChange,
  filteredPets,
  selectedPet,
  onSelectPet,
  onCancel,
  onNext,
}: PetSelectionStepProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Seleccionar paciente</h2>

      <div>
        <Input
          label="Buscar cliente"
          placeholder="Nombre, apellido o email..."
          value={clientSearch}
          onChange={(e) => {
            onClientSearchChange(e.target.value);
          }}
        />
        {clientSearch && !selectedClient && (
          <div className="mt-1 max-h-40 overflow-y-auto border border-gray-100 rounded-lg divide-y divide-gray-50">
            {filteredClients.slice(0, 8).map((c) => (
              <button
                key={c.id}
                onClick={() => onSelectClient(c)}
                className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50"
              >
                <span className="font-medium">{c.name} {c.surname}</span>
                <span className="text-gray-400 ml-2">{c.email}</span>
              </button>
            ))}
            {filteredClients.length === 0 && (
              <p className="px-3 py-2 text-sm text-gray-400">Sin resultados</p>
            )}
          </div>
        )}
      </div>

      {selectedClient && (
        <div>
          <Input
            label="Buscar mascota"
            placeholder="Nombre de la mascota..."
            value={petSearch}
            onChange={(e) => {
              onPetSearchChange(e.target.value);
            }}
          />
          {!selectedPet && (
            <div className="mt-1 max-h-40 overflow-y-auto border border-gray-100 rounded-lg divide-y divide-gray-50">
              {filteredPets.map((p) => (
                <button
                  key={p.id}
                  onClick={() => onSelectPet(p)}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50"
                >
                  <span className="font-medium">{p.name || "Sin nombre"}</span>
                  <span className="text-gray-400 ml-2">
                    {p.species} - {p.breed}
                  </span>
                </button>
              ))}
              {filteredPets.length === 0 && (
                <p className="px-3 py-2 text-sm text-gray-400">
                  Este cliente no tiene mascotas
                </p>
              )}
            </div>
          )}
        </div>
      )}

      <div className="flex gap-3 pt-2">
        <Button variant="ghost" onClick={onCancel}>Cancelar</Button>
        <div className="flex-1" />
        <Button onClick={onNext} disabled={!selectedPet}>
          Continuar
        </Button>
      </div>
    </div>
  );
}
