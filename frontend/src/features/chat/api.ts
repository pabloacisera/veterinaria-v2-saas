import { apiGet, apiPost } from "@/shared/lib/api";
import type { ChatQuota, ChatHistoryResponse } from "@/entities/chat/types";

export type { ChatQuota, ChatHistoryResponse };

export async function fetchCuota(): Promise<ChatQuota> {
  return apiGet<ChatQuota>("/chat/cuota");
}

export async function fetchHistorial(): Promise<ChatHistoryResponse> {
  return apiGet<ChatHistoryResponse>("/chat/historial");
}

export async function sendChatMessage(
  query: string,
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (error: string) => void,
): Promise<void> {
  const token = localStorage.getItem("access_token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  try {
    const res = await fetch("/api/v1/chat", {
      method: "POST",
      headers,
      body: JSON.stringify({ query }),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({ error: "Error del servidor" }));
      onError(data.error || data.detail || `Error ${res.status}`);
      return;
    }

    const reader = res.body?.getReader();
    if (!reader) {
      onError("No se pudo leer la respuesta");
      return;
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6).trim();
          if (data === "[DONE]") {
            onDone();
            return;
          }
          try {
            const parsed = JSON.parse(data);
            if (parsed.token) {
              onToken(parsed.token);
            }
          } catch {
            // skip malformed JSON
          }
        }
      }
    }
    onDone();
  } catch (err) {
    onError(err instanceof Error ? err.message : "Error de conexión");
  }
}
