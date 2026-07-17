import { useCuota } from "@/shared/hooks/useChat";

export function ChatQuotaBar() {
  const { data: quota, isLoading } = useCuota();

  if (isLoading) return null;
  if (!quota || quota.limite === 0) return null;

  const isUnlimited = quota.limite === -1;
  const percentage = quota.limite > 0 ? Math.round((quota.usado / quota.limite) * 100) : 0;
  const isExhausted = !isUnlimited && quota.usado >= quota.limite;

  return (
    <div className="px-4 py-3 border-b border-gray-100 bg-gray-50">
      <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
        <span>
          {isUnlimited
            ? "Requests ilimitados"
            : `${quota.usado}/${quota.limite} requests este mes`}
        </span>
        {!isUnlimited && (
          <span>
            Se renueva el {new Date(quota.reset_en).toLocaleDateString("es-AR")}
          </span>
        )}
      </div>
      {!isUnlimited && (
        <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              isExhausted ? "bg-red-500" : percentage > 80 ? "bg-yellow-500" : "bg-primary-500"
            }`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          />
        </div>
      )}
    </div>
  );
}
