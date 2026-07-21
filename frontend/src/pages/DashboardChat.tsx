import { useState, useCallback, useRef } from "react";
import type { ChatMessage } from "@/entities/chat/types";
import { ChatMessage as ChatMessageComponent } from "@/features/chat/ChatMessage";
import { ChatInput } from "@/features/chat/ChatInput";
import { ChatQuotaBar } from "@/features/chat/ChatQuotaBar";
import { ChatHistoryPanel } from "@/features/chat/ChatHistoryPanel";
import { sendChatMessage } from "@/features/chat/api";

let messageId = 0;
function nextId() {
  return `msg_${++messageId}_${Date.now()}`;
}

export function DashboardChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cuotaExhausted, setCuotaExhausted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 50);
  }, []);

  async function handleSend(query: string) {
    if (isLoading) return;
    setIsLoading(true);
    setError(null);

    const userMsg: ChatMessage = {
      id: nextId(),
      role: "user",
      content: query,
      timestamp: new Date().toISOString(),
    };

    const assistantMsg: ChatMessage = {
      id: nextId(),
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    scrollToBottom();

    await sendChatMessage(
      query,
      (token) => {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last && last.role === "assistant") {
            updated[updated.length - 1] = { ...last, content: last.content + token };
          }
          return updated;
        });
        scrollToBottom();
      },
      () => {
        setIsLoading(false);
      },
      (err) => {
        setIsLoading(false);
        setError(err);
        if (err.includes("cuota_agotada")) {
          setCuotaExhausted(true);
        }
        setMessages((prev) => prev.slice(0, -1));
      },
    );
  }

  function handleHistorySelect(historyMessages: ChatMessage[]) {
    setMessages(historyMessages);
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      <div className="hidden md:flex w-64 flex-shrink-0 flex-col bg-white rounded-2xl border border-gray-100">
        <div className="p-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Historial</h2>
        </div>
        <div className="flex-1 overflow-y-auto">
          <ChatHistoryPanel
            onSelect={handleHistorySelect}
            currentMessages={messages}
          />
        </div>
      </div>

      <div className="flex-1 flex flex-col bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <ChatQuotaBar />

        <div className="flex-1 overflow-y-auto p-4 space-y-1">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-2">
                <div className="text-4xl">🤖</div>
                <h2 className="text-lg font-semibold text-gray-900">
                  Asistente IA
                </h2>
                <p className="text-sm text-gray-500 max-w-md">
                  Hacé preguntas sobre tus clientes, mascotas, consultas,
                  insumos y más. El asistente tiene acceso a todos los datos
                  de tu veterinaria.
                </p>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id}>
              <ChatMessageComponent
                message={msg}
                isStreaming={
                  msg.role === "assistant" &&
                  msg === messages[messages.length - 1] &&
                  isLoading
                }
              />
            </div>
          ))}

          {error && (
            <div className="text-center py-2">
              <p className="text-sm text-red-500">{error}</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <ChatInput
          onSend={handleSend}
          disabled={isLoading || cuotaExhausted}
          placeholder={
            cuotaExhausted
              ? "Cuota agotada. Se renueva el próximo mes."
              : isLoading
              ? "Esperando respuesta..."
              : "Escribí tu mensaje..."
          }
        />
      </div>
    </div>
  );
}

export default DashboardChat;
