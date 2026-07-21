import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";
import { LoginForm } from "./LoginForm";
import * as api from "./api";

vi.mock("./api", () => ({
  loginUser: vi.fn(),
}));

function renderWithRouter(ui: React.ReactNode) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe("LoginForm", () => {
  afterEach(() => vi.clearAllMocks());

  it("renderiza campos email y password", () => {
    renderWithRouter(<LoginForm onSuccess={vi.fn()} />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /iniciar sesión/i })).toBeInTheDocument();
  });

  it("muestra error si los campos están vacíos", async () => {
    renderWithRouter(<LoginForm onSuccess={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: /iniciar sesión/i }));
    expect(await screen.findByText(/completá todos los campos/i)).toBeInTheDocument();
  });

  it("llama a loginUser con los datos correctos", async () => {
    const mockLogin = vi.mocked(api.loginUser).mockResolvedValue({
      access_token: "abc",
      refresh_token: "xyz",
      token_type: "bearer",
      expires_in: 3600,
    });
    const onSuccess = vi.fn();
    renderWithRouter(<LoginForm onSuccess={onSuccess} />);

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "test@test.com" } });
    fireEvent.change(screen.getByLabelText(/contraseña/i), { target: { value: "123456" } });
    fireEvent.click(screen.getByRole("button", { name: /iniciar sesión/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({ email: "test@test.com", password: "123456" });
      expect(onSuccess).toHaveBeenCalledWith("abc", 3600);
    });
  });

  it("muestra error del servidor en caso de fallo", async () => {
    vi.mocked(api.loginUser).mockRejectedValue(new Error("Credenciales inválidas"));
    renderWithRouter(<LoginForm onSuccess={vi.fn()} />);

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "test@test.com" } });
    fireEvent.change(screen.getByLabelText(/contraseña/i), { target: { value: "wrong" } });
    fireEvent.click(screen.getByRole("button", { name: /iniciar sesión/i }));

    expect(await screen.findByText(/credenciales inválidas/i)).toBeInTheDocument();
  });

  it("muestra link a registro", () => {
    renderWithRouter(<LoginForm onSuccess={vi.fn()} />);
    expect(screen.getByText(/registrarse/i)).toBeInTheDocument();
  });
});
