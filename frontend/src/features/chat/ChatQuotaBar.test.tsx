import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ChatQuotaBar } from "./ChatQuotaBar";

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
  fetchCuota: vi.fn(),
}));

import { fetchCuota } from "./api";

describe("ChatQuotaBar", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  it("muestra cuota cuando hay datos", async () => {
    vi.mocked(fetchCuota).mockResolvedValue({
      usado: 47,
      limite: 200,
      plan: "mensual",
      reset_en: "2026-07-01",
    });

    renderWithQC(<ChatQuotaBar />);

    await waitFor(() => {
      expect(screen.getByText(/47\/200/)).toBeInTheDocument();
    });
  });

  it("no renderiza nada cuando la cuota es 0", async () => {
    vi.mocked(fetchCuota).mockResolvedValue({
      usado: 0,
      limite: 0,
      plan: "",
      reset_en: "",
    });

    const { container } = renderWithQC(<ChatQuotaBar />);

    await waitFor(() => {
      expect(container.innerHTML).toBe("");
    });
  });

  it("muestra 'ilimitados' para plan anual", async () => {
    vi.mocked(fetchCuota).mockResolvedValue({
      usado: 0,
      limite: -1,
      plan: "anual",
      reset_en: "",
    });

    renderWithQC(<ChatQuotaBar />);

    await waitFor(() => {
      expect(screen.getByText(/Requests ilimitados/)).toBeInTheDocument();
    });
  });
});
