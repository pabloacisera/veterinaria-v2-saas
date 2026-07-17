import { render, screen, fireEvent } from "@testing-library/react";
import { Input } from "./Input";

describe("Input", () => {
  it("renderiza el input con label", () => {
    render(<Input label="Email" />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  });

  it("muestra error cuando se pasa error prop", () => {
    render(<Input label="Email" error="Email inválido" />);
    expect(screen.getByText(/email inválido/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toHaveClass("border-red-300");
  });

  it("no muestra error cuando no hay error", () => {
    render(<Input label="Email" />);
    expect(screen.queryByText(/email inválido/i)).not.toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).not.toHaveClass("border-red-300");
  });

  it("aplica id personalizado", () => {
    render(<Input id="custom-id" label="Test" />);
    expect(screen.getByLabelText(/test/i)).toHaveAttribute("id", "custom-id");
  });

  it("genera id automático desde label", () => {
    render(<Input label="Mi Campo" />);
    expect(screen.getByLabelText(/mi campo/i)).toHaveAttribute("id", "mi-campo");
  });

  it("maneja onChange correctamente", () => {
    const handleChange = vi.fn();
    render(<Input label="Test" onChange={handleChange} />);
    fireEvent.change(screen.getByLabelText(/test/i), { target: { value: "hello" } });
    expect(handleChange).toHaveBeenCalledTimes(1);
  });

  it("aplica className personalizada", () => {
    render(<Input label="Test" className="custom-input" />);
    expect(screen.getByLabelText(/test/i)).toHaveClass("custom-input");
  });

  it("renderiza placeholder", () => {
    render(<Input label="Test" placeholder="Escribí aquí" />);
    expect(screen.getByLabelText(/test/i)).toHaveAttribute("placeholder", "Escribí aquí");
  });

  it("renderiza type personalizado", () => {
    render(<Input label="Password" type="password" />);
    expect(screen.getByLabelText(/password/i)).toHaveAttribute("type", "password");
  });
});
