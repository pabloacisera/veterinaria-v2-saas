import { render, screen } from "@testing-library/react";
import { SubscriptionStatus } from "./SubscriptionStatus";

describe("SubscriptionStatus", () => {
  const defaultProps = {
    plan: "mensual",
    status: "activa",
    endDate: null,
    nextBilling: null,
  };

  it("renderiza el título Suscripción", () => {
    render(<SubscriptionStatus {...defaultProps} />);
    expect(screen.getByText("Suscripción")).toBeInTheDocument();
  });

  it("muestra el nombre del plan", () => {
    render(<SubscriptionStatus {...defaultProps} plan="anual" />);
    expect(screen.getByText("anual")).toBeInTheDocument();
  });

  it("muestra badge 'Activa' para status activa", () => {
    render(<SubscriptionStatus {...defaultProps} status="activa" />);
    expect(screen.getByText("Activa")).toBeInTheDocument();
  });

  it("muestra badge 'Período de prueba' para status trial", () => {
    render(<SubscriptionStatus {...defaultProps} status="trial" />);
    expect(screen.getByText("Período de prueba")).toBeInTheDocument();
  });

  it("muestra badge 'Vencida' para status vencida", () => {
    render(<SubscriptionStatus {...defaultProps} status="vencida" />);
    expect(screen.getByText("Vencida")).toBeInTheDocument();
  });

  it("muestra badge 'Bloqueada' para status bloqueada", () => {
    render(<SubscriptionStatus {...defaultProps} status="bloqueada" />);
    expect(screen.getByText("Bloqueada")).toBeInTheDocument();
  });

  it("muestra la fecha de vencimiento cuando endDate está presente", () => {
    render(<SubscriptionStatus {...defaultProps} endDate="2025-12-31T00:00:00Z" />);
    expect(screen.getByText("Vencimiento")).toBeInTheDocument();
  });

  it("muestra la fecha de próximo cobro cuando nextBilling está presente", () => {
    render(<SubscriptionStatus {...defaultProps} nextBilling="2025-02-01T00:00:00Z" />);
    expect(screen.getByText("Próximo cobro")).toBeInTheDocument();
  });

  it("no muestra vencimiento si endDate es null", () => {
    render(<SubscriptionStatus {...defaultProps} endDate={null} />);
    expect(screen.queryByText("Vencimiento")).not.toBeInTheDocument();
  });
});
