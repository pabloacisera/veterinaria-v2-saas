import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SaleWizard } from "./SaleWizard";

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

vi.mock("@/features/supplies/api", () => ({
  fetchSupplies: vi.fn(),
}));

vi.mock("@/shared/hooks/useClients", () => ({
  useClients: vi.fn(() => ({ data: [], isLoading: false })),
}));

vi.mock("./api", () => ({
  createSale: vi.fn(),
  saveDraft: vi.fn(),
  clearDraft: vi.fn(),
}));

import { fetchSupplies } from "@/features/supplies/api";
import { createSale, saveDraft, clearDraft } from "./api";

const mockSupplies = [
  { id: "s1", company_id: "c1", name: "Shampoo", brand: "PetCare", description: null, unit_base: "un", unit_price: 500, stock_quantity: 20, min_stock: 5, created_at: "2025-01-01", updated_at: "2025-01-01" },
  { id: "s2", company_id: "c1", name: "Alimento", brand: "Royal", description: null, unit_base: "kg", unit_price: 3000, stock_quantity: 10, min_stock: 3, created_at: "2025-01-01", updated_at: "2025-01-01" },
];

function stepHeading(name: string) {
  return screen.getByRole("heading", { name });
}

describe("SaleWizard", () => {
  const onComplete = vi.fn();
  const onCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
    vi.mocked(fetchSupplies).mockResolvedValue(mockSupplies);
    vi.mocked(saveDraft).mockResolvedValue(undefined as never);
    vi.mocked(clearDraft).mockResolvedValue(undefined as never);
    vi.mocked(createSale).mockResolvedValue({ id: "sale1" } as never);
  });

  it("renderiza el paso 1 (Cliente) con el título", () => {
    renderWithQC(<SaleWizard onComplete={onComplete} onCancel={onCancel} />);
    expect(stepHeading("Cliente")).toBeInTheDocument();
    expect(screen.getByText("Buscar cliente")).toBeInTheDocument();
  });

  it("navega entre pasos con botones Atrás y Continuar", async () => {
    const user = userEvent.setup();
    renderWithQC(<SaleWizard onComplete={onComplete} onCancel={onCancel} />);

    await user.click(screen.getByText("Continuar"));
    expect(saveDraft).toHaveBeenCalledWith(0, expect.any(Object));
    await waitFor(() => {
      expect(stepHeading("Insumos")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Atrás"));
    await waitFor(() => {
      expect(stepHeading("Cliente")).toBeInTheDocument();
    });
  });

  it("muestra botón Cancelar y llama a onCancel", async () => {
    const user = userEvent.setup();
    renderWithQC(<SaleWizard onComplete={onComplete} onCancel={onCancel} />);
    await user.click(screen.getByText("Cancelar"));
    expect(onCancel).toHaveBeenCalled();
  });

  it("pasa al paso de Pago cuando se agregan items", async () => {
    const user = userEvent.setup();
    renderWithQC(<SaleWizard onComplete={onComplete} onCancel={onCancel} />);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => {
      expect(stepHeading("Insumos")).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText("Escribí para buscar...");
    await user.type(searchInput, "Shampoo");
    await waitFor(() => {
      expect(screen.getByText("Shampoo")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Shampoo"));
    await user.click(screen.getByText("Agregar"));

    await waitFor(() => {
      expect(screen.getByText("Quitar")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => {
      expect(stepHeading("Pago")).toBeInTheDocument();
    });
  });

  it("renderiza opciones de método de pago en paso 3", async () => {
    const user = userEvent.setup();
    renderWithQC(<SaleWizard onComplete={onComplete} onCancel={onCancel} />);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Insumos")).toBeInTheDocument(); });

    const searchInput = screen.getByPlaceholderText("Escribí para buscar...");
    await user.type(searchInput, "Shampoo");
    await waitFor(() => { expect(screen.getByText("Shampoo")).toBeInTheDocument(); });
    await user.click(screen.getByText("Shampoo"));
    await user.click(screen.getByText("Agregar"));

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Pago")).toBeInTheDocument(); });

    const select = screen.getByRole("combobox");
    expect(select).toBeInTheDocument();
    expect(screen.getByText("Efectivo")).toBeInTheDocument();
    expect(screen.getByText("Transferencia")).toBeInTheDocument();
  });

  it("confirma la venta y llama a onComplete", async () => {
    const user = userEvent.setup();
    renderWithQC(<SaleWizard onComplete={onComplete} onCancel={onCancel} />);

    // Step 0 -> 1
    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Insumos")).toBeInTheDocument(); });

    // Add item
    const searchInput = screen.getByPlaceholderText("Escribí para buscar...");
    await user.type(searchInput, "Shampoo");
    await waitFor(() => { expect(screen.getByText("Shampoo")).toBeInTheDocument(); });
    await user.click(screen.getByText("Shampoo"));
    await user.click(screen.getByText("Agregar"));

    // Step 1 -> 2
    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Pago")).toBeInTheDocument(); });

    // Step 2 -> 3
    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Confirmar venta")).toBeInTheDocument(); });

    // Confirm
    await user.click(screen.getByRole("button", { name: "Confirmar venta" }));
    await waitFor(() => {
      expect(createSale).toHaveBeenCalled();
      expect(clearDraft).toHaveBeenCalled();
      expect(onComplete).toHaveBeenCalled();
    });
  });

  it("muestra error si createSale falla", async () => {
    vi.mocked(createSale).mockRejectedValue(new Error("fail"));
    const alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {});
    const user = userEvent.setup();
    renderWithQC(<SaleWizard onComplete={onComplete} onCancel={onCancel} />);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Insumos")).toBeInTheDocument(); });

    const searchInput = screen.getByPlaceholderText("Escribí para buscar...");
    await user.type(searchInput, "Shampoo");
    await waitFor(() => { expect(screen.getByText("Shampoo")).toBeInTheDocument(); });
    await user.click(screen.getByText("Shampoo"));
    await user.click(screen.getByText("Agregar"));

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Pago")).toBeInTheDocument(); });

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Confirmar venta")).toBeInTheDocument(); });

    await user.click(screen.getByRole("button", { name: "Confirmar venta" }));
    await waitFor(() => {
      expect(alertSpy).toHaveBeenCalledWith("Error al crear la venta");
    });
    alertSpy.mockRestore();
  });

  it("deshabilita Continuar si no hay items en paso de Insumos", async () => {
    const user = userEvent.setup();
    renderWithQC(<SaleWizard onComplete={onComplete} onCancel={onCancel} />);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Insumos")).toBeInTheDocument(); });

    const continueBtn = screen.getByText("Continuar");
    expect(continueBtn).toBeDisabled();
  });

  it("permite quitar un item de la lista", async () => {
    const user = userEvent.setup();
    renderWithQC(<SaleWizard onComplete={onComplete} onCancel={onCancel} />);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Insumos")).toBeInTheDocument(); });

    const searchInput = screen.getByPlaceholderText("Escribí para buscar...");
    await user.type(searchInput, "Shampoo");
    await waitFor(() => { expect(screen.getByText("Shampoo")).toBeInTheDocument(); });
    await user.click(screen.getByText("Shampoo"));
    await user.click(screen.getByText("Agregar"));

    await waitFor(() => { expect(screen.getByText("Quitar")).toBeInTheDocument(); });

    await user.click(screen.getByText("Quitar"));
    await waitFor(() => {
      expect(screen.queryByText("Quitar")).not.toBeInTheDocument();
    });
  });

  it("muestra resumen con IVA en paso de Confirmar", async () => {
    const user = userEvent.setup();
    renderWithQC(<SaleWizard onComplete={onComplete} onCancel={onCancel} />);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Insumos")).toBeInTheDocument(); });

    const searchInput = screen.getByPlaceholderText("Escribí para buscar...");
    await user.type(searchInput, "Shampoo");
    await waitFor(() => { expect(screen.getByText("Shampoo")).toBeInTheDocument(); });
    await user.click(screen.getByText("Shampoo"));
    await user.click(screen.getByText("Agregar"));

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Pago")).toBeInTheDocument(); });

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Confirmar venta")).toBeInTheDocument(); });

    expect(screen.getByText("Subtotal")).toBeInTheDocument();
    expect(screen.getByText("IVA (21%)")).toBeInTheDocument();
    expect(screen.getByText("Total")).toBeInTheDocument();
  });
});
