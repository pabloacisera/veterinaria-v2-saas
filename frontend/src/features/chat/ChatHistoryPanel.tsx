import { useHistorial } from "@/shared/hooks/useChat";
import type { ChatMessage } from "@/entities/chat/types";

interface ChatHistoryPanelProps {
  onSelect: (messages: ChatMessage[]) => void;
  currentMessages: ChatMessage[];
}

export function ChatHistoryPanel({ onSelect, currentMessages }: ChatHistoryPanelProps) {
  const { data: historyData, isLoading } = useHistorial();
  const history = historyData?.history ?? [];

  if (isLoading) {
    return (
      <div className="p-4 text-sm text-gray-500">Cargando historial...</div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="p-4 text-sm text-gray-500">
        No hay conversaciones previas
      </div>
    );
  }

  const conversations: { title: string; messages: ChatMessage[] }[] = [];
  let current: ChatMessage[] = [];

  for (const msg of history) {
    current.push(msg);
    if (msg.role === "assistant") {
      const userMsg = current.find((m) => m.role === "user");
      conversations.push({
        title: userMsg?.content.slice(0, 60) || "Conversación",
        messages: [...current],
      });
      current = [];
    }
  }

  return (
    <div className="space-y-1 p-2">
      {conversations.map((conv, i) => (
        <button
          key={i}
          onClick={() => onSelect(conv.messages)}
          className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
            currentMessages === conv.messages
              ? "bg-primary-50 text-primary-700"
              : "text-gray-600 hover:bg-gray-100"
          }`}
        >
          <p className="truncate font-medium">{conv.title}</p>
          <p className="text-xs text-gray-400 truncate">
            {conv.messages.length} mensajes
          </p>
        </button>
      ))}
    </div>
  );
}
