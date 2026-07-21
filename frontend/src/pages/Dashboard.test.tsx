import { vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "@/shared/lib/AuthContext";
import { Dashboard } from "./Dashboard";

vi.mock("@/features/clients/api", () => ({
  fetchClients: vi.fn().mockResolvedValue([]),
}));

const mockNavigate = vi.fn();

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

function renderDashboard(isAuthenticated: boolean) {
  if (!isAuthenticated) {
    localStorage.removeItem("auth_user");
    localStorage.removeItem("access_token");
  } else {
    localStorage.setItem("auth_user", JSON.stringify({ email: "test@test.com", name: "Test" }));
    localStorage.setItem("access_token", "token");
  }

  return render(
    <MemoryRouter initialEntries={["/dashboard"]}>
      <AuthProvider>
        <Dashboard />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("Dashboard auth guard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it("shows loading state initially", () => {
    renderDashboard(true);
    expect(screen.getByText("Cargando...")).toBeInTheDocument();
  });

  it("redirects to login when not authenticated", async () => {
    localStorage.removeItem("auth_user");
    localStorage.removeItem("access_token");
    renderDashboard(false);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/login");
    });
  });
});
