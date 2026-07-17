import { render, screen } from "@testing-library/react";
import { Badge } from "./Badge";

describe("Badge", () => {
  it("renderiza el texto del badge", () => {
    render(<Badge>Activo</Badge>);
    expect(screen.getByText(/activo/i)).toBeInTheDocument();
  });

  it("aplica variante default por defecto", () => {
    render(<Badge>Test</Badge>);
    const badge = screen.getByText(/test/i);
    expect(badge).toHaveClass("bg-gray-100");
    expect(badge).toHaveClass("text-gray-700");
  });

  it("aplica variante success", () => {
    render(<Badge variant="success">Éxito</Badge>);
    const badge = screen.getByText(/éxito/i);
    expect(badge).toHaveClass("bg-green-100");
    expect(badge).toHaveClass("text-green-700");
  });

  it("aplica variante warning", () => {
    render(<Badge variant="warning">Advertencia</Badge>);
    const badge = screen.getByText(/advertencia/i);
    expect(badge).toHaveClass("bg-yellow-100");
    expect(badge).toHaveClass("text-yellow-700");
  });

  it("aplica variante danger", () => {
    render(<Badge variant="danger">Peligro</Badge>);
    const badge = screen.getByText(/peligro/i);
    expect(badge).toHaveClass("bg-red-100");
    expect(badge).toHaveClass("text-red-700");
  });

  it("aplica clases base correctas", () => {
    render(<Badge>Test</Badge>);
    const badge = screen.getByText(/test/i);
    expect(badge).toHaveClass("inline-flex");
    expect(badge).toHaveClass("items-center");
    expect(badge).toHaveClass("px-2.5");
    expect(badge).toHaveClass("py-0.5");
    expect(badge).toHaveClass("rounded-full");
    expect(badge).toHaveClass("text-xs");
    expect(badge).toHaveClass("font-medium");
  });
});
