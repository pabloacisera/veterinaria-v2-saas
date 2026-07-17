import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import { ClienteAccesoForm } from "./ClienteAccesoForm";

const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

describe("ClienteAccesoForm", () => {
  afterEach(() => vi.clearAllMocks());

  it("renderiza el formulario con campos y botón", () => {
    render(<ClienteAccesoForm onSuccess={vi.fn()} />);
    expect(screen.getByLabelText(/código de acceso/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /ingresar/i })).toBeInTheDocument();
  });

  it("muestra error si el código está vacío", async () => {
    render(<ClienteAccesoForm onSuccess={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: /ingresar/i }));
    expect(await screen.findByText(/ingresá tu código de acceso/i)).toBeInTheDocument();
  });

  it("llama a onSuccess con token y nombre al enviar código válido", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ access_token: "token123", client_name: "Juan Pérez" }),
    });

    const onSuccess = vi.fn();
    render(<ClienteAccesoForm onSuccess={onSuccess} />);

    fireEvent.change(screen.getByLabelText(/código de acceso/i), { target: { value: "ABC123" } });
    fireEvent.click(screen.getByRole("button", { name: /ingresar/i }));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith("/api/v1/cliente/acceso", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ access_code: "ABC123" }),
      });
      expect(onSuccess).toHaveBeenCalledWith("token123", "Juan Pérez");
    });
  });

  it("muestra error del servidor si el código es inválido", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: "Código de acceso inválido" }),
    });

    render(<ClienteAccesoForm onSuccess={vi.fn()} />);

    fireEvent.change(screen.getByLabelText(/código de acceso/i), { target: { value: "INVALID" } });
    fireEvent.click(screen.getByRole("button", { name: /ingresar/i }));

    expect(await screen.findByText(/código de acceso inválido/i)).toBeInTheDocument();
  });
});
