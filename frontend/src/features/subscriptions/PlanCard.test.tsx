import { render, screen, fireEvent } from "@testing-library/react";
import { PlanCard } from "./PlanCard";

describe("PlanCard", () => {
  const defaultProps = {
    name: "Plan Mensual",
    price: "35000",
    period: "mes",
    features: ["200 consultas", "Soporte email"],
    onSelect: vi.fn(),
  };

  it("renderiza el nombre del plan", () => {
    render(<PlanCard {...defaultProps} />);
    expect(screen.getByText("Plan Mensual")).toBeInTheDocument();
  });

  it("renderiza el precio y período", () => {
    render(<PlanCard {...defaultProps} />);
    expect(screen.getByText("$35000")).toBeInTheDocument();
    expect(screen.getByText("/mes")).toBeInTheDocument();
  });

  it("renderiza la lista de features", () => {
    render(<PlanCard {...defaultProps} />);
    expect(screen.getByText("200 consultas")).toBeInTheDocument();
    expect(screen.getByText("Soporte email")).toBeInTheDocument();
  });

  it("muestra 'Suscribirme' cuando highlighted=true", () => {
    render(<PlanCard {...defaultProps} highlighted />);
    expect(screen.getByText("Suscribirme")).toBeInTheDocument();
  });

  it("muestra 'Elegir plan' cuando highlighted=false", () => {
    render(<PlanCard {...defaultProps} highlighted={false} />);
    expect(screen.getByText("Elegir plan")).toBeInTheDocument();
  });

  it("llama a onSelect al hacer click", () => {
    const onSelect = vi.fn();
    render(<PlanCard {...defaultProps} onSelect={onSelect} />);
    fireEvent.click(screen.getByRole("button"));
    expect(onSelect).toHaveBeenCalledTimes(1);
  });

  it("deshabilita el botón cuando loading=true", () => {
    render(<PlanCard {...defaultProps} loading />);
    expect(screen.getByRole("button")).toBeDisabled();
  });
});
