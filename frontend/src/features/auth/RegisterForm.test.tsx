import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";
import { RegisterForm } from "./RegisterForm";
import * as api from "./api";

vi.mock("./api", () => ({
  registerUser: vi.fn(),
}));

function renderWithRouter(ui: React.ReactNode) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe("RegisterForm", () => {
  afterEach(() => vi.clearAllMocks());

  it("renderiza el formulario completo", () => {
    renderWithRouter(<RegisterForm onSuccess={vi.fn()} />);
    expect(screen.getByPlaceholderText("Juan")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Pérez")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("juan@ejemplo.com")).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /crear cuenta/i })).toBeInTheDocument();
  }, 10000);

  it("llama a registerUser con datos válidos", async () => {
    const mockRegister = vi.mocked(api.registerUser).mockResolvedValue({
      id: "1",
      email: "test@test.com",
      name: "Juan",
      message: "Cuenta creada",
    });
    const onSuccess = vi.fn();
    renderWithRouter(<RegisterForm onSuccess={onSuccess} />);

    fireEvent.change(screen.getByPlaceholderText("Juan"), { target: { value: "Juan" } });
    fireEvent.change(screen.getByPlaceholderText("Pérez"), { target: { value: "Pérez" } });
    fireEvent.change(screen.getByPlaceholderText("juan@ejemplo.com"), { target: { value: "test@test.com" } });
    fireEvent.change(screen.getByLabelText(/contraseña/i), { target: { value: "123456" } });
    fireEvent.change(screen.getByPlaceholderText("Veterinaria San Martín"), { target: { value: "VetTest" } });
    fireEvent.change(screen.getByPlaceholderText("20-12345678-9"), { target: { value: "20-12345678-9" } });
    fireEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalled();
      expect(onSuccess).toHaveBeenCalledWith("test@test.com");
    });
  }, 10000);

  it("muestra error del servidor", async () => {
    vi.mocked(api.registerUser).mockRejectedValue(new Error("Email ya registrado"));
    renderWithRouter(<RegisterForm onSuccess={vi.fn()} />);

    fireEvent.change(screen.getByPlaceholderText("Juan"), { target: { value: "Juan" } });
    fireEvent.change(screen.getByPlaceholderText("Pérez"), { target: { value: "Pérez" } });
    fireEvent.change(screen.getByPlaceholderText("juan@ejemplo.com"), { target: { value: "test@test.com" } });
    fireEvent.change(screen.getByLabelText(/contraseña/i), { target: { value: "123456" } });
    fireEvent.change(screen.getByPlaceholderText("Veterinaria San Martín"), { target: { value: "VetTest" } });
    fireEvent.change(screen.getByPlaceholderText("20-12345678-9"), { target: { value: "20-12345678-9" } });
    fireEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));

    expect(await screen.findByText(/email ya registrado/i)).toBeInTheDocument();
  }, 10000);
});
