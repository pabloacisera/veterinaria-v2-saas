import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";
import { ActivateForm } from "./ActivateForm";
import * as api from "./api";

vi.mock("./api", () => ({
  activateAccount: vi.fn(),
}));

function renderWithRouter(ui: React.ReactNode) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe("ActivateForm", () => {
  afterEach(() => vi.clearAllMocks());

  it("renderiza el campo de código y muestra el email", () => {
    renderWithRouter(<ActivateForm email="test@test.com" />);
    expect(screen.getByText(/test@test.com/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/código de activación/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /activar cuenta/i })).toBeInTheDocument();
  });

  it("muestra error si el código está vacío", async () => {
    renderWithRouter(<ActivateForm email="test@test.com" />);
    fireEvent.click(screen.getByRole("button", { name: /activar cuenta/i }));
    expect(await screen.findByText(/ingresá el código de 6 dígitos/i)).toBeInTheDocument();
  });

  it("muestra error si el código tiene menos de 6 dígitos", async () => {
    renderWithRouter(<ActivateForm email="test@test.com" />);
    fireEvent.change(screen.getByLabelText(/código de activación/i), { target: { value: "12345" } });
    fireEvent.click(screen.getByRole("button", { name: /activar cuenta/i }));
    expect(await screen.findByText(/ingresá el código de 6 dígitos/i)).toBeInTheDocument();
  });

  it("llama a activateAccount con código válido", async () => {
    const mockActivate = vi.mocked(api.activateAccount).mockResolvedValue({ message: "Activada" });
    renderWithRouter(<ActivateForm email="test@test.com" />);

    fireEvent.change(screen.getByLabelText(/código de activación/i), { target: { value: "123456" } });
    fireEvent.click(screen.getByRole("button", { name: /activar cuenta/i }));

    await waitFor(() => {
      expect(mockActivate).toHaveBeenCalledWith({ email: "test@test.com", code: "123456" });
    });
  });

  it("muestra error del servidor", async () => {
    vi.mocked(api.activateAccount).mockRejectedValue(new Error("Código inválido o expirado"));
    renderWithRouter(<ActivateForm email="test@test.com" />);

    fireEvent.change(screen.getByLabelText(/código de activación/i), { target: { value: "999999" } });
    fireEvent.click(screen.getByRole("button", { name: /activar cuenta/i }));

    expect(await screen.findByText(/código inválido o expirado/i)).toBeInTheDocument();
  });

  it("muestra link para reintentar registro", () => {
    renderWithRouter(<ActivateForm email="test@test.com" />);
    expect(screen.getByText(/reintentar registro/i)).toBeInTheDocument();
  });
});
