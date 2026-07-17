import { useState, useEffect } from "react";
import { Modal } from "@/shared/ui/Modal";
import { Input } from "@/shared/ui/Input";
import { Button } from "@/shared/ui/Button";
import { useCreatePet, useUpdatePet } from "@/shared/hooks/usePets";
import type { PetData, CreatePetInput } from "./api";

interface PetFormProps {
  open: boolean;
  onClose: () => void;
  pet?: PetData | null;
}

export function PetForm({ open, onClose, pet }: PetFormProps) {
  const createMutation = useCreatePet();
  const updateMutation = useUpdatePet();
  const loading = createMutation.isPending || updateMutation.isPending;
  const [form, setForm] = useState<CreatePetInput>({
    name: "",
    species: "Perro",
    breed: "",
    sex: "Macho",
    color: "",
    birth_date: "",
    weight_kg: undefined,
    observations: "",
  });

  useEffect(() => {
    if (pet) {
      setForm({
        name: pet.name || "",
        species: pet.species || "Perro",
        breed: pet.breed || "",
        sex: pet.sex,
        color: pet.color || "",
        birth_date: pet.birth_date || "",
        weight_kg: pet.weight_kg || undefined,
        observations: pet.observations || "",
      });
    } else {
      setForm({
        name: "",
        species: "Perro",
        breed: "",
        sex: "Macho",
        color: "",
        birth_date: "",
        weight_kg: undefined,
        observations: "",
      });
    }
  }, [pet, open]);

  async function handleSubmit() {
    try {
      const payload = {
        ...form,
        birth_date: form.birth_date || undefined,
        weight_kg: form.weight_kg || undefined,
        observations: form.observations || undefined,
      };
      if (pet) {
        await updateMutation.mutateAsync({ id: pet.id, data: payload });
      } else {
        await createMutation.mutateAsync(payload);
      }
      onClose();
    } catch {
      alert("Error al guardar la mascota");
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={pet ? "Editar mascota" : "Nueva mascota"}
    >
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <Input
            label="Nombre"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
          <Input
            label="Especie"
            value={form.species}
            onChange={(e) => setForm({ ...form, species: e.target.value })}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Input
            label="Raza"
            value={form.breed}
            onChange={(e) => setForm({ ...form, breed: e.target.value })}
          />
          <Input
            label="Sexo"
            value={form.sex}
            onChange={(e) => setForm({ ...form, sex: e.target.value })}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Input
            label="Color"
            value={form.color}
            onChange={(e) => setForm({ ...form, color: e.target.value })}
          />
          <Input
            label="Peso (kg)"
            type="number"
            step="0.1"
            value={form.weight_kg ?? ""}
            onChange={(e) =>
              setForm({
                ...form,
                weight_kg: e.target.value ? Number(e.target.value) : undefined,
              })
            }
          />
        </div>
        <Input
          label="Fecha de nacimiento"
          type="date"
          value={form.birth_date}
          onChange={(e) => setForm({ ...form, birth_date: e.target.value })}
        />
        <Input
          label="Observaciones"
          value={form.observations}
          onChange={(e) => setForm({ ...form, observations: e.target.value })}
        />
        <div className="flex gap-3 pt-2">
          <Button variant="ghost" onClick={onClose} className="flex-1">
            Cancelar
          </Button>
          <Button
            className="flex-1"
            loading={loading}
            onClick={handleSubmit}
            disabled={!form.sex}
          >
            {pet ? "Guardar cambios" : "Crear mascota"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
