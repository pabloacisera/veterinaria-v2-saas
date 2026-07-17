import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AdminCompanyList } from "./AdminCompanyList";
import * as api from "./api";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

function renderWithQC(component: React.ReactNode) {
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
}

vi.mock("./api", () => ({
  fetchCompanias: vi.fn(),
  blockCompania: vi.fn(),
  unblockCompania: vi.fn(),
}));

const mockCompanies = {
  items: [
    {
      id: "1",
      cuit: "30-12345678-9",
      nombre: "Veterinaria San Martín",
      plan: "mensual",
      estado: "activa",
      inicio_suscripcion: "2025-01-01",
      fin_suscripcion: "2025-02-01",
      requests_usados: 42,
    },
    {
      id: "2",
      cuit: "30-87654321-9",
      nombre: "PetCare",
      plan: null,
      estado: "bloqueada",
      inicio_suscripcion: null,
      fin_suscripcion: null,
      requests_usados: 0,
    },
  ],
  total: 2,
  page: 1,
  page_size: 20,
};

describe("AdminCompanyList", () => {
  afterEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  it("carga y muestra compañías", async () => {
    vi.mocked(api.fetchCompanias).mockResolvedValue(mockCompanies);
    renderWithQC(<AdminCompanyList onSelect={vi.fn()} />);

    expect(await screen.findByText("Veterinaria San Martín")).toBeInTheDocument();
    expect(screen.getByText("PetCare")).toBeInTheDocument();
    expect(screen.getByText("30-12345678-9")).toBeInTheDocument();
  });

  it("muestra mensaje de vacío cuando no hay compañías", async () => {
    vi.mocked(api.fetchCompanias).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20 });
    renderWithQC(<AdminCompanyList onSelect={vi.fn()} />);

    expect(await screen.findByText("No se encontraron compañías")).toBeInTheDocument();
  });

  it("llama a blockCompania al bloquear y recarga", async () => {
    vi.mocked(api.fetchCompanias).mockResolvedValue(mockCompanies);
    vi.mocked(api.blockCompania).mockResolvedValue({ message: "Bloqueada" });

    renderWithQC(<AdminCompanyList onSelect={vi.fn()} />);
    expect(await screen.findByText("Veterinaria San Martín")).toBeInTheDocument();

    const blockButtons = screen.getAllByText("Bloquear");
    fireEvent.click(blockButtons[0]);

    await waitFor(() => {
      expect(api.blockCompania).toHaveBeenCalledWith("1");
    });
  });

  it("llama a unblockCompania al desbloquear y recarga", async () => {
    vi.mocked(api.fetchCompanias).mockResolvedValue(mockCompanies);
    vi.mocked(api.unblockCompania).mockResolvedValue({ message: "Desbloqueada" });

    renderWithQC(<AdminCompanyList onSelect={vi.fn()} />);
    expect(await screen.findByText("PetCare")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Desbloquear"));

    await waitFor(() => {
      expect(api.unblockCompania).toHaveBeenCalledWith("2");
    });
  });

  it("llama a onSelect al hacer click en Detalle", async () => {
    vi.mocked(api.fetchCompanias).mockResolvedValue(mockCompanies);
    const onSelect = vi.fn();

    renderWithQC(<AdminCompanyList onSelect={onSelect} />);
    expect(await screen.findByText("Veterinaria San Martín")).toBeInTheDocument();

    fireEvent.click(screen.getAllByText("Detalle")[0]);

    expect(onSelect).toHaveBeenCalledWith(mockCompanies.items[0]);
  });

  it("muestra paginación cuando hay más de 20 registros", async () => {
    vi.mocked(api.fetchCompanias).mockResolvedValue({
      items: Array.from({ length: 20 }, (_, i) => ({
        id: String(i),
        cuit: null,
        nombre: `Company ${i}`,
        plan: null,
        estado: "activa",
        inicio_suscripcion: null,
        fin_suscripcion: null,
        requests_usados: 0,
      })),
      total: 50,
      page: 1,
      page_size: 20,
    });

    renderWithQC(<AdminCompanyList onSelect={vi.fn()} />);
    expect(await screen.findByText("Siguiente")).toBeInTheDocument();
    expect(screen.getByText(/página 1 de 3/i)).toBeInTheDocument();
  });
});
