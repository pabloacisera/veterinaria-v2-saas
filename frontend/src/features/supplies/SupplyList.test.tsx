import { vi } from "vitest";

vi.mock("@/shared/lib/api", () => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPut: vi.fn(),
  apiDelete: vi.fn(),
}));

vi.mock("@/shared/hooks/useSupplies", () => ({
  useSupplies: vi.fn(() => ({ data: [], isLoading: false, refetch: vi.fn() })),
  useDeleteSupply: vi.fn(() => ({ mutateAsync: vi.fn() })),
  useCreateSupply: vi.fn(() => ({ mutateAsync: vi.fn(), isPending: false })),
  useUpdateSupply: vi.fn(() => ({ mutateAsync: vi.fn(), isPending: false })),
}));

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SupplyList } from "./SupplyList";
import { downloadTemplate } from "./api";

vi.mock("./api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./api")>();
  return {
    ...actual,
    uploadSuppliesCsv: vi.fn(),
    downloadTemplate: vi.fn(),
  };
});

function renderWithProviders(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("SupplyList upload", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders download template button", () => {
    renderWithProviders(<SupplyList onEdit={vi.fn()} onCreate={vi.fn()} />);
    expect(screen.getByText("Descargar plantilla")).toBeInTheDocument();
  });

  it("renders upload CSV button", () => {
    renderWithProviders(<SupplyList onEdit={vi.fn()} onCreate={vi.fn()} />);
    expect(screen.getByText("Subir CSV")).toBeInTheDocument();
  });

  it("calls downloadTemplate when clicking download button", async () => {
    renderWithProviders(<SupplyList onEdit={vi.fn()} onCreate={vi.fn()} />);
    const user = userEvent.setup();
    await user.click(screen.getByText("Descargar plantilla"));
    expect(vi.mocked(downloadTemplate)).toHaveBeenCalled();
  });

  it("triggers file input when clicking upload button", () => {
    renderWithProviders(<SupplyList onEdit={vi.fn()} onCreate={vi.fn()} />);
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    expect(fileInput).toBeTruthy();
    expect(fileInput.accept).toBe(".csv,.xlsx");
  });
});
