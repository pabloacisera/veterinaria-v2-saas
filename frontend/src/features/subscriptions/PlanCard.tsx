import { Button } from "@/shared/ui/Button";

interface PlanCardProps {
  name: string;
  price: string;
  period: string;
  features: string[];
  highlighted?: boolean;
  onSelect: () => void;
  loading?: boolean;
}

export function PlanCard({
  name,
  price,
  period,
  features,
  highlighted,
  onSelect,
  loading,
}: PlanCardProps) {
  return (
    <div
      className={`rounded-xl border-2 p-6 ${
        highlighted
          ? "border-primary-500 bg-primary-50/50 shadow-md"
          : "border-gray-200 bg-white"
      }`}
    >
      <h3 className="text-lg font-bold text-gray-900">{name}</h3>
      <div className="mt-3">
        <span className="text-3xl font-bold text-gray-900">${price}</span>
        <span className="text-gray-500 text-sm ml-1">/{period}</span>
      </div>
      <ul className="mt-4 space-y-2">
        {features.map((f, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
            <span className="text-primary-500 mt-0.5">✓</span>
            {f}
          </li>
        ))}
      </ul>
      <div className="mt-6">
        <Button onClick={onSelect} loading={loading} className="w-full">
          {highlighted ? "Suscribirme" : "Elegir plan"}
        </Button>
      </div>
    </div>
  );
}
