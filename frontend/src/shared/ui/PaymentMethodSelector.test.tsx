import { render, screen, fireEvent } from "@testing-library/react";
import { PaymentMethodSelector } from "@/shared/ui/PaymentMethodSelector";

describe("PaymentMethodSelector", () => {
  const defaultProps = {
    value: "efectivo",
    onChange: vi.fn(),
  };

  it("renderiza el label Método de pago", () => {
    render(<PaymentMethodSelector {...defaultProps} />);
    expect(screen.getByText("Método de pago")).toBeInTheDocument();
  });

  it("muestra las 3 opciones de pago", () => {
    render(<PaymentMethodSelector {...defaultProps} />);
    expect(screen.getByText("Efectivo")).toBeInTheDocument();
    expect(screen.getByText("Transferencia")).toBeInTheDocument();
    expect(screen.getByText("QR (Mercado Pago)")).toBeInTheDocument();
  });

  it("llama a onChange al seleccionar un método", () => {
    const onChange = vi.fn();
    render(<PaymentMethodSelector {...defaultProps} onChange={onChange} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "transferencia" } });
    expect(onChange).toHaveBeenCalledWith("transferencia");
  });

  it("muestra QR cuando value=qr y qrData presente", () => {
    render(<PaymentMethodSelector value="qr" onChange={vi.fn()} qrData="test-qr-data" />);
    expect(screen.getByText("Escaneá este código QR para pagar")).toBeInTheDocument();
    expect(screen.getByAltText("Código QR de pago")).toBeInTheDocument();
  });

  it("muestra mensaje placeholder cuando value=qr pero sin qrData", () => {
    render(<PaymentMethodSelector value="qr" onChange={vi.fn()} qrData={null} />);
    expect(
      screen.getByText("El código QR se generará al confirmar la operación.")
    ).toBeInTheDocument();
  });

  it("no muestra QR cuando value no es qr", () => {
    render(<PaymentMethodSelector value="efectivo" onChange={vi.fn()} qrData="some-data" />);
    expect(
      screen.queryByText("Escaneá este código QR para pagar")
    ).not.toBeInTheDocument();
  });
});
