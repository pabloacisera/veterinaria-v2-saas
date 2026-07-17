import { useState } from "react";
import { CashMovementList } from "@/features/cash/CashMovementList";
import { CashMovementForm } from "@/features/cash/CashMovementForm";

export function DashboardCaja() {
  const [formOpen, setFormOpen] = useState(false);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Caja</h1>
      <CashMovementList onCreate={() => setFormOpen(true)} />
      <CashMovementForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
      />
    </div>
  );
}
