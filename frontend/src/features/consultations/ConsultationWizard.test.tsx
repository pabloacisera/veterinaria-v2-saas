import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ConsultationWizard } from "./ConsultationWizard";

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

vi.mock("@/features/clients/api", () => ({
  fetchClients: vi.fn(),
}));

vi.mock("@/features/pets/api", () => ({
  fetchPets: vi.fn(),
}));

vi.mock("@/features/supplies/api", () => ({
  fetchSupplies: vi.fn(),
  fetchProcedures: vi.fn(),
}));

vi.mock("./api", () => ({
  createConsultation: vi.fn(),
  addProcedures: vi.fn(),
  addSupplies: vi.fn(),
  saveConsultationDraft: vi.fn(),
  clearConsultationDraft: vi.fn(),
}));

import { fetchClients } from "@/features/clients/api";
import { fetchPets } from "@/features/pets/api";
import { fetchSupplies, fetchProcedures } from "@/features/supplies/api";
import {
  createConsultation,
  addProcedures,
  addSupplies,
  clearConsultationDraft,
} from "./api";

const mockClients = [
  { id: "cl1", company_id: "c1", name: "Juan", surname: "Pérez", doc_type: "DNI", doc_number: "12345", email: "juan@test.com", phone: null, address: null, city: null, created_at: "2025-01-01", updated_at: "2025-01-01" },
];

const mockPets = [
  { id: "p1", company_id: "c1", owner_id: "cl1", name: "Max", species: "Perro", breed: "Labrador", sex: "Macho", birth_date: null, weight_kg: 25, color: "Dorado", observations: null, photo_urls: [], created_at: "2025-01-01", updated_at: "2025-01-01" },
];

const mockProcedures = [
  { id: "pr1", company_id: "c1", name: "Vacunación", description: null, price: 5000, created_at: "2025-01-01", updated_at: "2025-01-01" },
];

const mockSupplies = [
  { id: "s1", company_id: "c1", name: "Antibiótico", brand: null, description: null, unit_base: "un", unit_price: 1500, stock_quantity: 10, min_stock: 2, created_at: "2025-01-01", updated_at: "2025-01-01" },
];

function stepHeading(name: string) {
  return screen.getByRole("heading", { name });
}

async function selectClientAndPet(user: ReturnType<typeof userEvent.setup>) {
  const clientSearch = screen.getByPlaceholderText("Nombre, apellido o email...");
  await user.type(clientSearch, "Juan");
  await waitFor(() => {
    expect(screen.getByRole("button", { name: /Juan Pérez/ })).toBeInTheDocument();
  });
  await user.click(screen.getByRole("button", { name: /Juan Pérez/ }));
  await waitFor(() => {
    expect(screen.getByRole("button", { name: /Max/ })).toBeInTheDocument();
  });
  await user.click(screen.getByRole("button", { name: /Max/ }));
}

describe("ConsultationWizard", () => {
  const onComplete = vi.fn();
  const onCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
    vi.mocked(fetchClients).mockResolvedValue({ items: mockClients, total: 1, offset: 0, limit: 100 });
    vi.mocked(fetchPets).mockResolvedValue({ items: mockPets, total: 1, offset: 0, limit: 100 });
    vi.mocked(fetchSupplies).mockResolvedValue({ items: mockSupplies, total: 1, offset: 0, limit: 100 });
    vi.mocked(fetchProcedures).mockResolvedValue({ items: mockProcedures, total: 1, offset: 0, limit: 100 });
    vi.mocked(createConsultation).mockResolvedValue({ id: "con1" } as never);
    vi.mocked(addProcedures).mockResolvedValue(undefined as never);
    vi.mocked(addSupplies).mockResolvedValue(undefined as never);
    vi.mocked(clearConsultationDraft).mockResolvedValue(undefined as never);
  });

  it("renderiza el paso de selección de paciente", () => {
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);
    expect(stepHeading("Seleccionar paciente")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Nombre, apellido o email...")).toBeInTheDocument();
  });

  it("permite buscar y seleccionar un cliente", async () => {
    const user = userEvent.setup();
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);

    const searchInput = screen.getByPlaceholderText("Nombre, apellido o email...");
    await user.type(searchInput, "Juan");
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Juan Pérez/ })).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /Juan Pérez/ }));
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Max/ })).toBeInTheDocument();
    });
  });

  it("permite buscar y seleccionar una mascota después de seleccionar cliente", async () => {
    const user = userEvent.setup();
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);

    await selectClientAndPet(user);

    await waitFor(() => {
      const continueBtn = screen.getByText("Continuar");
      expect(continueBtn).not.toBeDisabled();
    });
  });

  it("deshabilita Continuar si no hay mascota seleccionada", async () => {
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);
    const continueBtn = screen.getByText("Continuar");
    expect(continueBtn).toBeDisabled();
  });

  it("navega al paso de consulta después de seleccionar mascota", async () => {
    const user = userEvent.setup();
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);

    await selectClientAndPet(user);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => {
      expect(stepHeading("Datos de la consulta")).toBeInTheDocument();
      expect(screen.getByText("Motivo de consulta")).toBeInTheDocument();
    });
  });

  it("muestra nombre del paciente en paso de consulta", async () => {
    const user = userEvent.setup();
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);

    await selectClientAndPet(user);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => {
      expect(screen.getByText(/Max/)).toBeInTheDocument();
    });
  });

  it("deshabilita Continuar si falta motivo o diagnóstico", async () => {
    const user = userEvent.setup();
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);

    await selectClientAndPet(user);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Datos de la consulta")).toBeInTheDocument(); });

    const continueBtn = screen.getByText("Continuar");
    expect(continueBtn).toBeDisabled();
  });

  it("permite avanzar a procedimientos cuando motivo y diagnóstico están completos", async () => {
    const user = userEvent.setup();
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);

    await selectClientAndPet(user);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Datos de la consulta")).toBeInTheDocument(); });

    await user.type(screen.getByLabelText("Motivo de consulta"), "Dolor estomacal");
    await user.type(screen.getByLabelText("Diagnóstico"), "Gastritis");

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => {
      expect(stepHeading("Procedimientos")).toBeInTheDocument();
    });
  });

  it("permite agregar y quitar procedimientos", async () => {
    const user = userEvent.setup();
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);

    await selectClientAndPet(user);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Datos de la consulta")).toBeInTheDocument(); });

    await user.type(screen.getByLabelText("Motivo de consulta"), "Dolor");
    await user.type(screen.getByLabelText("Diagnóstico"), "Gastritis");

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Procedimientos")).toBeInTheDocument(); });

    const procSearch = screen.getByPlaceholderText("Buscar...");
    await user.type(procSearch, "Vacunación");
    await waitFor(() => { expect(screen.getByText("Vacunación")).toBeInTheDocument(); });

    await user.click(screen.getByText("Vacunación"));
    await waitFor(() => { expect(screen.getByText("Quitar")).toBeInTheDocument(); });

    await user.click(screen.getByText("Quitar"));
    await waitFor(() => { expect(screen.queryByText("Quitar")).not.toBeInTheDocument(); });
  });

  it("confirma la consulta y llama a onComplete", async () => {
    const user = userEvent.setup();
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);

    await selectClientAndPet(user);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Datos de la consulta")).toBeInTheDocument(); });

    await user.type(screen.getByLabelText("Motivo de consulta"), "Dolor");
    await user.type(screen.getByLabelText("Diagnóstico"), "Gastritis");

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Procedimientos")).toBeInTheDocument(); });

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Insumos")).toBeInTheDocument(); });

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Método de pago")).toBeInTheDocument(); });

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Confirmar consulta")).toBeInTheDocument(); });

    await user.click(screen.getByRole("button", { name: "Confirmar consulta" }));
    await waitFor(() => {
      expect(createConsultation).toHaveBeenCalledWith({
        pet_id: "p1",
        reason: "Dolor",
        diagnosis: "Gastritis",
        treatment: undefined,
      });
      expect(clearConsultationDraft).toHaveBeenCalled();
      expect(onComplete).toHaveBeenCalled();
    });
  });

  it("muestra error si createConsultation falla", async () => {
    vi.mocked(createConsultation).mockRejectedValue(new Error("fail"));
    const alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {});
    const user = userEvent.setup();
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);

    await selectClientAndPet(user);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Datos de la consulta")).toBeInTheDocument(); });
    await user.type(screen.getByLabelText("Motivo de consulta"), "Dolor");
    await user.type(screen.getByLabelText("Diagnóstico"), "Gastritis");

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Procedimientos")).toBeInTheDocument(); });
    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Insumos")).toBeInTheDocument(); });
    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Método de pago")).toBeInTheDocument(); });
    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Confirmar consulta")).toBeInTheDocument(); });

    await user.click(screen.getByRole("button", { name: "Confirmar consulta" }));
    await waitFor(() => {
      expect(alertSpy).toHaveBeenCalledWith("Error al crear la consulta");
    });
    alertSpy.mockRestore();
  });

  it("llama a onCancel al hacer click en Cancelar", async () => {
    const user = userEvent.setup();
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);
    await user.click(screen.getByText("Cancelar"));
    expect(onCancel).toHaveBeenCalled();
  });

  it("permite navegar hacia atrás entre pasos", async () => {
    const user = userEvent.setup();
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);

    await selectClientAndPet(user);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Datos de la consulta")).toBeInTheDocument(); });

    await user.click(screen.getByText("Atrás"));
    await waitFor(() => { expect(stepHeading("Seleccionar paciente")).toBeInTheDocument(); });
  });

  it("muestra datos del paciente en paso de confirmación", async () => {
    const user = userEvent.setup();
    renderWithQC(<ConsultationWizard onComplete={onComplete} onCancel={onCancel} />);

    await selectClientAndPet(user);

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Datos de la consulta")).toBeInTheDocument(); });
    await user.type(screen.getByLabelText("Motivo de consulta"), "Dolor");
    await user.type(screen.getByLabelText("Diagnóstico"), "Gastritis");

    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Procedimientos")).toBeInTheDocument(); });
    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Insumos")).toBeInTheDocument(); });
    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Método de pago")).toBeInTheDocument(); });
    await user.click(screen.getByText("Continuar"));
    await waitFor(() => { expect(stepHeading("Confirmar consulta")).toBeInTheDocument(); });

    expect(screen.getAllByText("Paciente").length).toBeGreaterThan(0);
    expect(screen.getByText("Max")).toBeInTheDocument();
    expect(screen.getByText("Dolor")).toBeInTheDocument();
    expect(screen.getByText("Gastritis")).toBeInTheDocument();
  });
});
