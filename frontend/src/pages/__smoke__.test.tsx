import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/shared/lib/AuthContext";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

vi.mock("@/shared/lib/api", () => ({
  apiGet: vi.fn().mockResolvedValue([]),
  apiGetBlob: vi.fn().mockResolvedValue(new Blob()),
  apiPost: vi.fn().mockResolvedValue({}),
  apiPut: vi.fn().mockResolvedValue({}),
  apiDelete: vi.fn().mockResolvedValue(undefined),
}));

import { Landing } from "./Landing";
import { Login } from "./Login";
import { Register } from "./Register";
import { DashboardHome } from "./DashboardHome";
import { DashboardClients } from "./DashboardClients";
import { DashboardPets } from "./DashboardPets";
import { DashboardInsumos } from "./DashboardInsumos";
import { DashboardCaja } from "./DashboardCaja";
import { DashboardTienda } from "./DashboardTienda";
import { DashboardConsultas } from "./DashboardConsultas";

function renderWithRouter(component: React.ReactNode, initialEntries = ["/"]) {
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <MemoryRouter initialEntries={initialEntries}>
          {component}
        </MemoryRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

describe("Smoke tests: Landing", () => {
  it("renderiza sin errores", () => {
    renderWithRouter(<Landing />);
    expect(screen.getByText("Veter")).toBeInTheDocument();
    expect(screen.getByText("Gestioná tu veterinaria")).toBeInTheDocument();
  });

  it("muestra botones de login y registro", () => {
    renderWithRouter(<Landing />);
    expect(screen.getByText("Iniciar sesión")).toBeInTheDocument();
    expect(screen.getByText("Registrarse")).toBeInTheDocument();
  });

  it("muestra las 3 features", () => {
    renderWithRouter(<Landing />);
    expect(screen.getByText("Clientes y Mascotas")).toBeInTheDocument();
    expect(screen.getByText("Consultas y Facturación")).toBeInTheDocument();
    expect(screen.getByText("Stock y Caja")).toBeInTheDocument();
  });
});

describe("Smoke tests: Login", () => {
  it("renderiza sin errores", () => {
    renderWithRouter(<Login />);
    expect(screen.getAllByText("Iniciar sesión").length).toBeGreaterThan(0);
  });

  it("muestra formulario de login", () => {
    renderWithRouter(<Login />);
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Contraseña")).toBeInTheDocument();
  });

  it("muestra mensaje de cuenta activada", () => {
    renderWithRouter(<Login />, ["/login?activated=true"]);
    expect(screen.getByText(/Cuenta activada correctamente/)).toBeInTheDocument();
  });
});

describe("Smoke tests: Register", () => {
  it("renderiza sin errores", () => {
    renderWithRouter(<Register />);
    expect(screen.getAllByText("Crear cuenta").length).toBeGreaterThan(0);
  });

  it("muestra formulario de registro", () => {
    renderWithRouter(<Register />);
    expect(screen.getByLabelText("Nombre")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
  });
});

describe("Smoke tests: DashboardHome", () => {
  beforeEach(() => {
    localStorage.setItem("access_token", "test-token");
  });

  it("renderiza sin errores", () => {
    renderWithRouter(<DashboardHome />);
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });

  it("muestra stat cards", () => {
    renderWithRouter(<DashboardHome />);
    expect(screen.getByText("Clientes")).toBeInTheDocument();
    expect(screen.getByText("Mascotas")).toBeInTheDocument();
    expect(screen.getByText("Consultas")).toBeInTheDocument();
    expect(screen.getByText("Caja")).toBeInTheDocument();
  });

  it("muestra acciones rápidas", () => {
    renderWithRouter(<DashboardHome />);
    expect(screen.getByText("Nuevo cliente")).toBeInTheDocument();
    expect(screen.getByText("Nueva mascota")).toBeInTheDocument();
    expect(screen.getByText("Nueva consulta")).toBeInTheDocument();
    expect(screen.getByText("Nueva venta")).toBeInTheDocument();
  });
});

describe("Smoke tests: DashboardClients", () => {
  beforeEach(() => {
    localStorage.setItem("access_token", "test-token");
  });

  it("renderiza sin errores", () => {
    renderWithRouter(<DashboardClients />);
    expect(screen.getByText("Clientes")).toBeInTheDocument();
  });
});

describe("Smoke tests: DashboardPets", () => {
  beforeEach(() => {
    localStorage.setItem("access_token", "test-token");
  });

  it("renderiza sin errores", () => {
    renderWithRouter(<DashboardPets />);
    expect(screen.getByText("Mascotas")).toBeInTheDocument();
  });
});

describe("Smoke tests: DashboardInsumos", () => {
  beforeEach(() => {
    localStorage.setItem("access_token", "test-token");
  });

  it("renderiza sin errores", () => {
    renderWithRouter(<DashboardInsumos />);
    expect(screen.getByText("Insumos")).toBeInTheDocument();
  });
});

describe("Smoke tests: DashboardCaja", () => {
  beforeEach(() => {
    localStorage.setItem("access_token", "test-token");
  });

  it("renderiza sin errores", () => {
    renderWithRouter(<DashboardCaja />);
    expect(screen.getByText("Caja")).toBeInTheDocument();
  });
});

describe("Smoke tests: DashboardTienda", () => {
  beforeEach(() => {
    localStorage.setItem("access_token", "test-token");
  });

  it("renderiza sin errores", () => {
    renderWithRouter(<DashboardTienda />);
    expect(screen.getByText("Tienda")).toBeInTheDocument();
  });

  it("muestra botón nueva venta", () => {
    renderWithRouter(<DashboardTienda />);
    expect(screen.getByText("Nueva venta")).toBeInTheDocument();
  });
});

describe("Smoke tests: DashboardConsultas", () => {
  beforeEach(() => {
    localStorage.setItem("access_token", "test-token");
  });

  it("renderiza sin errores", () => {
    renderWithRouter(<DashboardConsultas />);
    expect(screen.getByText("Consultas")).toBeInTheDocument();
  });

  it("muestra botón nueva consulta", () => {
    renderWithRouter(<DashboardConsultas />);
    expect(screen.getByText("Nueva consulta")).toBeInTheDocument();
  });
});
