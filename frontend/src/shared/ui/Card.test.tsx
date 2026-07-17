import { render, screen } from "@testing-library/react";
import { Card } from "./Card";

describe("Card", () => {
  it("renderiza los children", () => {
    render(<Card>Contenido de la card</Card>);
    expect(screen.getByText(/contenido de la card/i)).toBeInTheDocument();
  });

  it("aplica clases base correctas", () => {
    render(<Card data-testid="card">Test</Card>);
    const card = screen.getByTestId("card");
    expect(card).toHaveClass("bg-white");
    expect(card).toHaveClass("rounded-2xl");
    expect(card).toHaveClass("shadow-sm");
    expect(card).toHaveClass("border");
    expect(card).toHaveClass("border-gray-100");
    expect(card).toHaveClass("p-8");
  });

  it("aplica className personalizada", () => {
    render(<Card className="custom-card" data-testid="card">Test</Card>);
    const card = screen.getByTestId("card");
    expect(card).toHaveClass("custom-card");
  });

  it("renderiza children complejos", () => {
    render(
      <Card>
        <h1 className="text-xl">Título</h1>
        <p className="text-gray-500">Descripción</p>
      </Card>
    );
    expect(screen.getByText(/título/i)).toBeInTheDocument();
    expect(screen.getByText(/descripción/i)).toBeInTheDocument();
  });
});
