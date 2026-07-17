import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import { DocumentDownloadButton } from "./DocumentDownloadButton";

vi.mock("@/shared/lib/api", () => ({
  apiGetBlob: vi.fn(),
}));

import { apiGetBlob } from "@/shared/lib/api";

describe("DocumentDownloadButton", () => {
  afterEach(() => {
    vi.clearAllMocks();
    document.body.innerHTML = "";
  });

  const defaultProps = {
    entityId: "e123",
    entityType: "consulta" as const,
    documentType: "factura" as const,
  };

  it("renderiza botón con texto según documentType factura", () => {
    render(<DocumentDownloadButton {...defaultProps} />);
    expect(screen.getByText("Descargar factura")).toBeInTheDocument();
  });

  it("renderiza botón con texto según documentType prescripcion", () => {
    render(<DocumentDownloadButton {...defaultProps} documentType="prescripcion" />);
    expect(screen.getByText("Descargar prescripción")).toBeInTheDocument();
  });

  it("muestra loading mientras descarga", async () => {
    vi.mocked(apiGetBlob).mockReturnValue(new Promise(() => {}));
    render(<DocumentDownloadButton {...defaultProps} />);

    fireEvent.click(screen.getByText("Descargar factura"));

    expect(await screen.findByRole("button")).toBeDisabled();
  });

  it("descarga el PDF y lo agrega al DOM", async () => {
    const blob = new Blob(["PDF"], { type: "application/pdf" });
    vi.mocked(apiGetBlob).mockResolvedValue(blob);

    const createObjectURL = vi.fn(() => "blob:url");
    const revokeObjectURL = vi.fn();
    URL.createObjectURL = createObjectURL;
    URL.revokeObjectURL = revokeObjectURL;

    const appendChild = vi.spyOn(document.body, "appendChild");
    const removeChild = vi.spyOn(document.body, "removeChild");

    render(<DocumentDownloadButton {...defaultProps} />);
    fireEvent.click(screen.getByText("Descargar factura"));

    await waitFor(() => {
      expect(vi.mocked(apiGetBlob)).toHaveBeenCalledWith(
        "/consulta/e123/factura/download"
      );
      expect(appendChild).toHaveBeenCalled();
      expect(removeChild).toHaveBeenCalled();
      expect(revokeObjectURL).toHaveBeenCalled();
    });
  });

  it("muestra error cuando la descarga falla", async () => {
    vi.mocked(apiGetBlob).mockRejectedValue(new Error("Documento no encontrado"));

    render(<DocumentDownloadButton {...defaultProps} />);
    fireEvent.click(screen.getByText("Descargar factura"));

    expect(await screen.findByText("Documento no encontrado")).toBeInTheDocument();
  });

  it("muestra botón de reintentar cuando hay error", async () => {
    vi.mocked(apiGetBlob)
      .mockRejectedValueOnce(new Error("Error"))
      .mockResolvedValueOnce(new Blob(["PDF"], { type: "application/pdf" }));

    render(<DocumentDownloadButton {...defaultProps} />);
    fireEvent.click(screen.getByText("Descargar factura"));

    expect(await screen.findByText("Error")).toBeInTheDocument();
    expect(screen.getByText("Reintentar")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Reintentar"));

    await waitFor(() => {
      expect(vi.mocked(apiGetBlob)).toHaveBeenCalledTimes(2);
    });
  });

  it("usa filename personalizado cuando se proporciona", async () => {
    const blob = new Blob(["PDF"], { type: "application/pdf" });
    vi.mocked(apiGetBlob).mockResolvedValue(blob);

    const createObjectURL = vi.fn(() => "blob:url");
    URL.createObjectURL = createObjectURL;
    URL.revokeObjectURL = vi.fn();

    let appendedAnchor: HTMLAnchorElement | null = null;
    const origAppendChild = Node.prototype.appendChild;
    const appendChild = vi.spyOn(document.body, "appendChild").mockImplementation(function (child) {
      if (child instanceof HTMLAnchorElement) {
        appendedAnchor = child;
      }
      return origAppendChild.call(this, child);
    });

    render(
      <DocumentDownloadButton {...defaultProps} filename="mi-factura.pdf" />
    );
    fireEvent.click(screen.getByText("Descargar factura"));

    await waitFor(() => {
      expect(appendedAnchor?.download).toBe("mi-factura.pdf");
    });

    appendChild.mockRestore();
  });
});
