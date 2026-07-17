import { render, screen, fireEvent } from "@testing-library/react";
import { vi } from "vitest";
import { ClienteFacturas } from "./ClienteFacturas";
import type { Factura } from "@/entities/client-portal";

const facturas: Factura[] = [
  {
    id: "f1",
    entity_type: "consulta",
    entity_id: "e1",
    download_url: "https://example.com/pdf/1",
    version: 1,
    created_at: "2025-03-15T10:00:00Z",
  },
  {
    id: "f2",
    entity_type: "venta",
    entity_id: "e2",
    download_url: null,
    version: 2,
    created_at: "2025-03-20T14:30:00Z",
    pending_payment: {
      amount: 15000.5,
      payment_method: "mercadopago",
      status: "pending",
    },
  },
];

describe("ClienteFacturas", () => {
  it("muestra loading cuando loading=true", () => {
    render(<ClienteFacturas facturas={[]} loading={true} />);
    expect(screen.getByText(/cargando facturas/i)).toBeInTheDocument();
  });

  it("muestra mensaje vacío cuando no hay facturas", () => {
    render(<ClienteFacturas facturas={[]} loading={false} />);
    expect(screen.getByText(/no hay facturas disponibles/i)).toBeInTheDocument();
  });

  it("renderiza lista de facturas", () => {
    render(<ClienteFacturas facturas={facturas} loading={false} />);
    expect(screen.getByText(/factura #1/i)).toBeInTheDocument();
    expect(screen.getByText(/factura #2/i)).toBeInTheDocument();
  });

  it("muestra etiqueta de pago pendiente cuando corresponde", () => {
    render(<ClienteFacturas facturas={facturas} loading={false} />);
    expect(screen.getByText(/pago pendiente/i)).toBeInTheDocument();
    expect(screen.getByText(/15000\.50/)).toBeInTheDocument();
  });

  it("muestra botón de descarga cuando hay download_url", () => {
    render(<ClienteFacturas facturas={facturas} loading={false} />);
    const downloadButtons = screen.getAllByText("Descargar");
    expect(downloadButtons).toHaveLength(1);
  });

  it("solo muestra botón de descarga en facturas con download_url", () => {
    render(<ClienteFacturas facturas={facturas} loading={false} />);
    expect(screen.getAllByText("Descargar")).toHaveLength(1);
  });

  it("abre el PDF en nueva pestaña al hacer click en descargar", () => {
    const open = vi.fn();
    vi.stubGlobal("open", open);

    render(<ClienteFacturas facturas={facturas} loading={false} />);
    fireEvent.click(screen.getByText("Descargar"));

    expect(open).toHaveBeenCalledWith("https://example.com/pdf/1", "_blank");

    vi.unstubAllGlobals();
  });
});
