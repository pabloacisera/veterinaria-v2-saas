import { vi } from "vitest";

vi.mock("@/shared/lib/api", () => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPut: vi.fn(),
  apiDelete: vi.fn(),
}));

vi.mock("@/shared/hooks/useSupplies", () => ({
  useSupplies: vi.fn(() => ({ data: { items: [], total_count: 0 }, isLoading: false, refetch: vi.fn() })),
  useDeleteSupply: vi.fn(() => ({ mutateAsync: vi.fn() })),
  useCreateSupply: vi.fn(() => ({ mutateAsync: vi.fn(), isPending: false })),
  useUpdateSupply: vi.fn(() => ({ mutateAsync: vi.fn(), isPending: false })),
}));

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SupplyList } from "./SupplyList";
import { downloadTemplate, uploadSuppliesCsv } from "./api";

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

  it("shows success message after successful upload", async () => {
    vi.mocked(uploadSuppliesCsv).mockResolvedValue({ created: 3, errors: [] });
    renderWithProviders(<SupplyList onEdit={vi.fn()} onCreate={vi.fn()} />);
    const user = userEvent.setup();
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(["test"], "test.csv", { type: "text/csv" });
    await user.upload(fileInput, file);
    await waitFor(() => {
      expect(screen.getByText("3 insumos creados correctamente")).toBeInTheDocument();
    });
  });

  it("shows error message after failed upload", async () => {
    vi.mocked(uploadSuppliesCsv).mockRejectedValue(new Error("Token de acceso requerido"));
    renderWithProviders(<SupplyList onEdit={vi.fn()} onCreate={vi.fn()} />);
    const user = userEvent.setup();
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(["test"], "test.csv", { type: "text/csv" });
    await user.upload(fileInput, file);
    await waitFor(() => {
      expect(screen.getByText("Token de acceso requerido")).toBeInTheDocument();
    });
  });
});
