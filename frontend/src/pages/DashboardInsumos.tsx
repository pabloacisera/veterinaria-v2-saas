import { useState } from "react";
import { SupplyList } from "@/features/supplies/SupplyList";
import { SupplyForm } from "@/features/supplies/SupplyForm";
import type { SupplyData } from "@/entities/supply/types";

export function DashboardInsumos() {
  const [formOpen, setFormOpen] = useState(false);
  const [editingSupply, setEditingSupply] = useState<SupplyData | null>(null);

  function handleEdit(supply: SupplyData) {
    setEditingSupply(supply);
    setFormOpen(true);
  }

  function handleCreate() {
    setEditingSupply(null);
    setFormOpen(true);
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Insumos</h1>
      <SupplyList
        onEdit={handleEdit}
        onCreate={handleCreate}
      />
      <SupplyForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        supply={editingSupply}
      />
    </div>
  );
}

export default DashboardInsumos;
