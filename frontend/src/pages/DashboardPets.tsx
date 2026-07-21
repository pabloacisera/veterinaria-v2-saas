import { useState } from "react";
import { PetList } from "@/features/pets/PetList";
import { PetForm } from "@/features/pets/PetForm";
import type { PetData } from "@/entities/pet/types";

export function DashboardPets() {
  const [formOpen, setFormOpen] = useState(false);
  const [editingPet, setEditingPet] = useState<PetData | null>(null);

  function handleEdit(pet: PetData) {
    setEditingPet(pet);
    setFormOpen(true);
  }

  function handleCreate() {
    setEditingPet(null);
    setFormOpen(true);
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Mascotas</h1>
      <PetList
        onEdit={handleEdit}
        onCreate={handleCreate}
      />
      <PetForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        pet={editingPet}
      />
    </div>
  );
}
