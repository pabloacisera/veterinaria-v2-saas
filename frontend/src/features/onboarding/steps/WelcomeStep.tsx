import { Button } from "@/shared/ui/Button";

interface WelcomeStepProps {
  onStart: () => void;
}

export function WelcomeStep({ onStart }: WelcomeStepProps) {
  return (
    <div className="text-center space-y-4">
      <div className="text-5xl">👋</div>
      <h2 className="text-2xl font-bold text-gray-900">¡Bienvenido a Veter!</h2>
      <p className="text-gray-500">
        En unos pasos vamos a configurar tu veterinaria. Primero,
        registrá tu primer cliente y su mascota para empezar a usar el sistema.
      </p>
      <Button size="lg" onClick={onStart} className="mt-4">Comenzar</Button>
    </div>
  );
}
