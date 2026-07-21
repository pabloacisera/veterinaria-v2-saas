import { vi } from "vitest";

vi.mock("@/shared/hooks/useSupplies", () => ({
  useCreateSupply: vi.fn(() => ({ mutateAsync: vi.fn(), isPending: false })),
  useUpdateSupply: vi.fn(() => ({ mutateAsync: vi.fn(), isPending: false })),
}));

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SupplyForm } from "./SupplyForm";
import { useCreateSupply } from "@/shared/hooks/useSupplies";

describe("SupplyForm zero value handling", () => {
  beforeEach(() => vi.clearAllMocks());

  it("does not drop zero values when submitting", async () => {
    const createMutate = vi.fn().mockResolvedValue({});
    vi.mocked(useCreateSupply).mockReturnValue({
      mutateAsync: createMutate,
      isPending: false,
    } as ReturnType<typeof useCreateSupply>);

    const user = userEvent.setup();
    render(<SupplyForm open={true} onClose={vi.fn()} />);

    const priceInput = screen.getByLabelText("Precio unitario");
    await user.clear(priceInput);
    await user.type(priceInput, "0");

    const stockInput = screen.getByLabelText("Stock");
    await user.clear(stockInput);
    await user.type(stockInput, "0");

    const nameInput = screen.getByLabelText("Nombre");
    await user.type(nameInput, "Test Supply");

    await user.click(screen.getByText("Crear insumo"));

    await waitFor(() => {
      expect(createMutate).toHaveBeenCalled();
    });

    const payload = createMutate.mock.calls[0][0];
    expect(payload.unit_price).toBe(0);
    expect(payload.stock_quantity).toBe(0);
    expect(payload.name).toBe("Test Supply");
  });

  it("preserves zero min_stock in payload", async () => {
    const createMutate = vi.fn().mockResolvedValue({});
    vi.mocked(useCreateSupply).mockReturnValue({
      mutateAsync: createMutate,
      isPending: false,
    } as ReturnType<typeof useCreateSupply>);

    const user = userEvent.setup();
    render(<SupplyForm open={true} onClose={vi.fn()} />);

    const nameInput = screen.getByLabelText("Nombre");
    await user.type(nameInput, "Test");

    const minStockInput = screen.getByLabelText("Stock mínimo");
    await user.clear(minStockInput);
    await user.type(minStockInput, "0");

    await user.click(screen.getByText("Crear insumo"));

    await waitFor(() => {
      expect(createMutate).toHaveBeenCalled();
    });

    const payload = createMutate.mock.calls[0][0];
    expect(payload.min_stock).toBe(0);
  });
});
