import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MercadoPagoConnect } from "./MercadoPagoConnect";

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
  fetchOAuthStatus: vi.fn(),
  initOAuth: vi.fn(),
}));

import { fetchOAuthStatus, initOAuth } from "./api";

describe("MercadoPagoConnect", () => {
  afterEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  it("muestra loading inicialmente", () => {
    vi.mocked(fetchOAuthStatus).mockReturnValue(new Promise(() => {}));
    renderWithQC(<MercadoPagoConnect />);
    expect(screen.getByText("Cargando...")).toBeInTheDocument();
  });

  it("muestra 'Desconectado' cuando no está conectado", async () => {
    vi.mocked(fetchOAuthStatus).mockResolvedValue({ conectado: false, mp_user_id: null });
    renderWithQC(<MercadoPagoConnect />);
    await waitFor(() => {
      expect(screen.getByText("Desconectado")).toBeInTheDocument();
    });
  });

  it("muestra 'Conectado' cuando está conectado", async () => {
    vi.mocked(fetchOAuthStatus).mockResolvedValue({ conectado: true, mp_user_id: "mp-user-123" });
    renderWithQC(<MercadoPagoConnect />);
    await waitFor(() => {
      expect(screen.getByText("Conectado")).toBeInTheDocument();
    });
  });

  it("muestra mp_user_id cuando conectado", async () => {
    vi.mocked(fetchOAuthStatus).mockResolvedValue({ conectado: true, mp_user_id: "mp-user-123" });
    renderWithQC(<MercadoPagoConnect />);
    await waitFor(() => {
      expect(screen.getByText("mp-user-123")).toBeInTheDocument();
    });
  });

  it("muestra botón 'Conectar Mercado Pago' cuando desconectado", async () => {
    vi.mocked(fetchOAuthStatus).mockResolvedValue({ conectado: false, mp_user_id: null });
    renderWithQC(<MercadoPagoConnect />);
    await waitFor(() => {
      expect(screen.getByText("Conectar Mercado Pago")).toBeInTheDocument();
    });
  });

  it("llama a initOAuth al hacer click en conectar", async () => {
    vi.mocked(fetchOAuthStatus).mockResolvedValue({ conectado: false, mp_user_id: null });
    const originalLocation = window.location;
    delete window.location;
    window.location = { href: "" } as any;
    vi.mocked(initOAuth).mockResolvedValue({ auth_url: "https://mp.com/auth" });

    renderWithQC(<MercadoPagoConnect />);
    await waitFor(() => {
      expect(screen.getByText("Conectar Mercado Pago")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText("Conectar Mercado Pago"));
    await waitFor(() => {
      expect(initOAuth).toHaveBeenCalledTimes(1);
    });
    window.location = originalLocation;
  });
});
