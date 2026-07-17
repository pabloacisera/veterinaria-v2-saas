export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface ChatQuota {
  usado: number;
  limite: number;
  plan: string;
  reset_en: string;
}

export interface ChatHistoryResponse {
  history: ChatMessage[];
}
