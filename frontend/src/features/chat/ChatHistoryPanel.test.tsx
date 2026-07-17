import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ChatHistoryPanel } from "./ChatHistoryPanel";
import type { ChatMessage } from "@/entities/chat/types";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

function renderWithQC(component: React.ReactNode) {
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
}

vi.mock("./api", () => ({
  fetchHistorial: vi.fn(),
}));

import { fetchHistorial } from "./api";

const mockHistory: ChatMessage[] = [
  {
    id: "1",
    role: "user",
    content: "¿Qué sabes sobre mi veterinaria?",
    timestamp: "2026-06-24T12:00:00Z",
  },
  {
    id: "2",
    role: "assistant",
    content: "Tengo información sobre tus datos.",
    timestamp: "2026-06-24T12:00:05Z",
  },
];

describe("ChatHistoryPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  it("muestra historial cuando hay datos", async () => {
    vi.mocked(fetchHistorial).mockResolvedValue({ history: mockHistory });

    renderWithQC(
      <ChatHistoryPanel onSelect={() => {}} currentMessages={[]} />
    );

    await waitFor(() => {
      expect(screen.getByText(/¿Qué sabes sobre mi veterinaria/)).toBeInTheDocument();
    });
  });

  it("muestra mensaje vacio cuando no hay historial", async () => {
    vi.mocked(fetchHistorial).mockResolvedValue({ history: [] });

    renderWithQC(
      <ChatHistoryPanel onSelect={() => {}} currentMessages={[]} />
    );

    await waitFor(() => {
      expect(screen.getByText("No hay conversaciones previas")).toBeInTheDocument();
    });
  });

  it("llama a onSelect al hacer click en una conversación", async () => {
    vi.mocked(fetchHistorial).mockResolvedValue({ history: mockHistory });
    const onSelect = vi.fn();

    renderWithQC(
      <ChatHistoryPanel onSelect={onSelect} currentMessages={[]} />
    );

    await waitFor(() => {
      expect(screen.getByText(/¿Qué sabes sobre mi veterinaria/)).toBeInTheDocument();
    });

    screen.getByText(/¿Qué sabes sobre mi veterinaria/).click();
    expect(onSelect).toHaveBeenCalled();
  });
});
