import { Button } from "@/shared/ui/Button";

interface DoneStepProps {
  onComplete: () => void;
}

export function DoneStep({ onComplete }: DoneStepProps) {
  return (
    <div className="text-center space-y-4">
      <div className="text-5xl">🎉</div>
      <h2 className="text-2xl font-bold text-gray-900">¡Todo listo!</h2>
      <p className="text-gray-500">
        Ya podés empezar a usar Veter. Explorá el panel para gestionar clientes, mascotas, consultas y más.
      </p>
      <Button size="lg" onClick={onComplete}>Ir al Dashboard</Button>
    </div>
  );
}
