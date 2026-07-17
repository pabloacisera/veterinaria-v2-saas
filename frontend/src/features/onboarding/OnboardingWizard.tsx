import { useState } from "react";
import { Card } from "@/shared/ui/Card";
import { useCreateClient } from "@/shared/hooks/useClients";
import { useCreatePet } from "@/shared/hooks/usePets";
import { WelcomeStep } from "./steps/WelcomeStep";
import { FirstClientStep } from "./steps/FirstClientStep";
import { FirstPetStep } from "./steps/FirstPetStep";
import { DoneStep } from "./steps/DoneStep";

interface OnboardingWizardProps {
  onComplete: () => void;
}

export function OnboardingWizard({ onComplete }: OnboardingWizardProps) {
  const [step, setStep] = useState(0);
  const createClientMutation = useCreateClient();
  const createPetMutation = useCreatePet();

  const [clientData, setClientData] = useState({
    name: "",
    surname: "",
    email: "",
    doc_type: "DNI",
    doc_number: "",
    phone: "",
  });
  const [petData, setPetData] = useState({
    name: "",
    species: "Perro",
    breed: "",
    sex: "Macho",
    color: "",
    birth_date: "",
  });
  const [newClientId, setNewClientId] = useState<string | null>(null);

  const steps = [
    { title: "Bienvenido", description: "Configuración inicial" },
    { title: "Primer cliente", description: "Registrá tu primer cliente" },
    { title: "Primera mascota", description: "Registrá la primera mascota" },
    { title: "¡Listo!", description: "Todo configurado" },
  ];

  async function handleCreateClient() {
    try {
      const client = await createClientMutation.mutateAsync({
        name: clientData.name,
        surname: clientData.surname,
        email: clientData.email,
        doc_type: clientData.doc_type,
        doc_number: clientData.doc_number,
        phone: clientData.phone || undefined,
      });
      setNewClientId(client.id);
      setStep(2);
    } catch {
      alert("Error al crear el cliente. Verificá los datos.");
    }
  }

  async function handleCreatePet() {
    if (!newClientId) {
      setStep(3);
      return;
    }
    try {
      await createPetMutation.mutateAsync({
        owner_id: newClientId,
        name: petData.name || undefined,
        species: petData.species || undefined,
        breed: petData.breed || undefined,
        sex: petData.sex,
        color: petData.color || undefined,
        birth_date: petData.birth_date || undefined,
      });
      setStep(3);
    } catch {
      setStep(3);
    }
  }

  function handleSkipPet() {
    setStep(3);
  }

  function handleComplete() {
    localStorage.setItem("onboarding_done", "true");
    onComplete();
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-lg">
        <div className="flex items-center justify-center gap-2 mb-6">
          {steps.map((s, i) => (
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
              {i < steps.length - 1 && (
                <div
                  className={`w-8 h-0.5 ${i < step ? "bg-primary-600" : "bg-gray-200"}`}
                />
              )}
            </div>
          ))}
        </div>

        <Card>
          {step === 0 && <WelcomeStep onStart={() => setStep(1)} />}

          {step === 1 && (
            <FirstClientStep
              clientData={clientData}
              onClientDataChange={setClientData}
              loading={createClientMutation.isPending}
              onSave={handleCreateClient}
              onSkip={() => { setNewClientId(null); setStep(3); }}
            />
          )}

          {step === 2 && (
            <FirstPetStep
              petData={petData}
              onPetDataChange={setPetData}
              loading={createPetMutation.isPending}
              onSave={handleCreatePet}
              onSkip={handleSkipPet}
            />
          )}

          {step === 3 && <DoneStep onComplete={handleComplete} />}
        </Card>
      </div>
    </div>
  );
}
