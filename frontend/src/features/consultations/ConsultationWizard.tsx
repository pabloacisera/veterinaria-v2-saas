import { useState } from "react";
import { Card } from "@/shared/ui/Card";
import { useClients } from "@/shared/hooks/useClients";
import { usePets } from "@/shared/hooks/usePets";
import { useSupplies, useProcedures } from "@/shared/hooks/useSupplies";
import { useCreateConsultation } from "@/shared/hooks/useConsultations";
import type { ClientData } from "@/entities/client/types";
import type { PetData } from "@/entities/pet/types";
import type { SupplyData, ProcedureData } from "@/entities/supply/types";
import { apiPost } from "@/shared/lib/api";
import { PetSelectionStep } from "./steps/PetSelectionStep";
import { ConsultationDataStep } from "./steps/ConsultationDataStep";
import { ProceduresStep } from "./steps/ProceduresStep";
import { SuppliesStep } from "./steps/SuppliesStep";
import { PaymentStep } from "./steps/PaymentStep";
import { ConfirmationStep } from "./steps/ConfirmationStep";
import { QrStep } from "./steps/QrStep";

interface ConsultationWizardProps {
  onComplete: () => void;
  onCancel: () => void;
}

export function ConsultationWizard({ onComplete, onCancel }: ConsultationWizardProps) {
  const [step, setStep] = useState(0);
  const { data: clientsData } = useClients({ limit: 100 });
  const allClients = clientsData?.items ?? [];
  const { data: petsData } = usePets({ limit: 100 });
  const allPets = petsData?.items ?? [];
  const { data: proceduresData } = useProcedures(100);
  const allProcedures = proceduresData?.items ?? [];
  const { data: suppliesData } = useSupplies({ limit: 100 });
  const allSupplies = suppliesData?.items ?? [];
  const createConsultationMutation = useCreateConsultation();

  const [clientSearch, setClientSearch] = useState("");
  const [selectedClient, setSelectedClient] = useState<ClientData | null>(null);

  const [selectedPet, setSelectedPet] = useState<PetData | null>(null);
  const [petSearch, setPetSearch] = useState("");

  const [reason, setReason] = useState("");
  const [diagnosis, setDiagnosis] = useState("");
  const [treatment, setTreatment] = useState("");

  const [selectedProcedures, setSelectedProcedures] = useState<{ proc: ProcedureData; quantity: number }[]>([]);
  const [selectedSupplies, setSelectedSupplies] = useState<{ supply: SupplyData; quantity: number }[]>([]);

  const [paymentMethod, setPaymentMethod] = useState("efectivo");
  const [qrData, setQrData] = useState<string | null>(null);

  const [procedureSearch, setProcedureSearch] = useState("");
  const [supplySearch, setSupplySearch] = useState("");

  const filteredClients = allClients.filter(
    (c) =>
      `${c.name} ${c.surname}`.toLowerCase().includes(clientSearch.toLowerCase()) ||
      c.email.toLowerCase().includes(clientSearch.toLowerCase())
  );

  const filteredPets = allPets.filter(
    (p) => (p.name || "").toLowerCase().includes(petSearch.toLowerCase()) &&
      (!selectedClient || p.owner_id === selectedClient.id)
  );

  const filteredProcedures = allProcedures.filter(
    (p) => p.name.toLowerCase().includes(procedureSearch.toLowerCase())
  );

  const filteredSupplies = allSupplies.filter(
    (s) => s.name.toLowerCase().includes(supplySearch.toLowerCase())
  );

  function addProcedure(proc: ProcedureData) {
    setSelectedProcedures([...selectedProcedures, { proc, quantity: 1 }]);
    setProcedureSearch("");
  }

  function removeProcedure(index: number) {
    setSelectedProcedures(selectedProcedures.filter((_, i) => i !== index));
  }

  function addSupply(supply: SupplyData) {
    setSelectedSupplies([...selectedSupplies, { supply, quantity: 1 }]);
    setSupplySearch("");
  }

  function removeSupply(index: number) {
    setSelectedSupplies(selectedSupplies.filter((_, i) => i !== index));
  }

  async function handleConfirm() {
    if (!selectedPet) return;
    try {
      const consultation = await createConsultationMutation.mutateAsync({
        pet_id: selectedPet.id,
        reason,
        diagnosis,
        treatment: treatment || undefined,
      });

      if (selectedProcedures.length > 0) {
        const { addProcedures } = await import("./api");
        await addProcedures(
          consultation.id,
          selectedProcedures.map((p) => ({
            procedure_id: p.proc.id,
            quantity: p.quantity,
          }))
        );
      }

      if (selectedSupplies.length > 0) {
        const { addSupplies } = await import("./api");
        await addSupplies(
          consultation.id,
          selectedSupplies.map((s) => ({
            supply_id: s.supply.id,
            quantity: s.quantity,
          }))
        );
      }

      if (paymentMethod !== "efectivo" && grandTotal > 0) {
        try {
          const paymentResult = await apiPost<{ movimiento_id: string; qr_data?: string }>(
            `/pagos/consulta/${consultation.id}`,
            { metodo: paymentMethod, monto: grandTotal }
          );
          if (paymentResult.qr_data) {
            setQrData(paymentResult.qr_data);
            setStep(5);
            return;
          }
        } catch {
          // payment creation is optional
        }
      }

      const { clearConsultationDraft } = await import("./api");
      await clearConsultationDraft();
      onComplete();
    } catch {
      alert("Error al crear la consulta");
    }
  }

  const totalProcedures = selectedProcedures.reduce(
    (sum, p) => sum + p.quantity * Number(p.proc.price),
    0
  );
  const totalSupplies = selectedSupplies.reduce(
    (sum, s) => sum + s.quantity * Number(s.supply.unit_price),
    0
  );
  const grandTotal = totalProcedures + totalSupplies;

  const steps = ["Paciente", "Consulta", "Procedimientos", "Insumos", "Pago", "Confirmar"];
  const maxStep = qrData ? 6 : 5;

  return (
    <Card>
      <div className="flex items-center justify-center gap-2 mb-6">
        {steps.slice(0, maxStep).map((s, i) => (
          <div key={i} className="flex items-center gap-2">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                i <= step
                  ? "bg-primary-600 text-white"
                  : "bg-gray-200 text-gray-400"
              }`}
            >
              {i < step ? "✓" : i + 1}
            </div>
            <span className={`text-sm hidden sm:inline ${i <= step ? "text-gray-900 font-medium" : "text-gray-400"}`}>
              {s}
            </span>
            {i < maxStep - 1 && (
              <div
                className={`w-6 h-0.5 ${i < step ? "bg-primary-600" : "bg-gray-200"}`}
              />
            )}
          </div>
        ))}
      </div>

      {step === 0 && (
        <PetSelectionStep
          clientSearch={clientSearch}
          onClientSearchChange={(v) => {
            setClientSearch(v);
            setSelectedClient(null);
            setSelectedPet(null);
          }}
          filteredClients={filteredClients}
          selectedClient={selectedClient}
          onSelectClient={(c) => {
            setSelectedClient(c);
            setClientSearch(`${c.name} ${c.surname}`);
          }}
          petSearch={petSearch}
          onPetSearchChange={(v) => {
            setPetSearch(v);
            setSelectedPet(null);
          }}
          filteredPets={filteredPets}
          selectedPet={selectedPet}
          onSelectPet={(p) => {
            setSelectedPet(p);
            setPetSearch(p.name || "");
          }}
          onCancel={onCancel}
          onNext={() => setStep(1)}
        />
      )}

      {step === 1 && (
        <ConsultationDataStep
          selectedPet={selectedPet}
          selectedClient={selectedClient}
          reason={reason}
          onReasonChange={setReason}
          diagnosis={diagnosis}
          onDiagnosisChange={setDiagnosis}
          treatment={treatment}
          onTreatmentChange={setTreatment}
          onBack={() => setStep(0)}
          onNext={() => setStep(2)}
        />
      )}

      {step === 2 && (
        <ProceduresStep
          procedureSearch={procedureSearch}
          onProcedureSearchChange={setProcedureSearch}
          filteredProcedures={filteredProcedures}
          selectedProcedures={selectedProcedures}
          onAddProcedure={addProcedure}
          onRemoveProcedure={removeProcedure}
          onProcedureQuantityChange={(i, q) => {
            const newItems = [...selectedProcedures];
            newItems[i].quantity = q;
            setSelectedProcedures(newItems);
          }}
          onBack={() => setStep(1)}
          onNext={() => setStep(3)}
        />
      )}

      {step === 3 && (
        <SuppliesStep
          supplySearch={supplySearch}
          onSupplySearchChange={setSupplySearch}
          filteredSupplies={filteredSupplies}
          selectedSupplies={selectedSupplies}
          onAddSupply={addSupply}
          onRemoveSupply={removeSupply}
          onSupplyQuantityChange={(i, q) => {
            const newItems = [...selectedSupplies];
            newItems[i].quantity = q;
            setSelectedSupplies(newItems);
          }}
          onBack={() => setStep(2)}
          onNext={() => setStep(4)}
        />
      )}

      {step === 4 && (
        <PaymentStep
          paymentMethod={paymentMethod}
          onPaymentMethodChange={setPaymentMethod}
          qrData={qrData}
          onQrDataChange={setQrData}
          totalProcedures={totalProcedures}
          totalSupplies={totalSupplies}
          grandTotal={grandTotal}
          onBack={() => setStep(3)}
          onNext={() => setStep(5)}
        />
      )}

      {step === 6 && qrData && (
        <QrStep qrData={qrData} onComplete={onComplete} />
      )}

      {step === 5 && (
        <ConfirmationStep
          selectedPet={selectedPet}
          selectedClient={selectedClient}
          reason={reason}
          diagnosis={diagnosis}
          treatment={treatment}
          selectedProcedures={selectedProcedures}
          selectedSupplies={selectedSupplies}
          totalProcedures={totalProcedures}
          totalSupplies={totalSupplies}
          grandTotal={grandTotal}
          loading={createConsultationMutation.isPending}
          onBack={() => setStep(4)}
          onConfirm={handleConfirm}
        />
      )}
    </Card>
  );
}
