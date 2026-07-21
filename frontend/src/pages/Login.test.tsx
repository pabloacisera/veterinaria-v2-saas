import { vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "@/shared/lib/AuthContext";
import { Login } from "./Login";

vi.mock("@/features/auth/api", () => ({
  fetchCurrentUser: vi.fn(),
}));

vi.mock("@/features/auth/LoginForm", () => ({
  LoginForm: ({ onSuccess }: { onSuccess: (t: string) => void }) => (
    <button onClick={() => onSuccess("test-token")}>Mock LoginForm</button>
  ),
}));

function renderWithProviders(
  initialEntries: string[] = ["/login"]
) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <AuthProvider>
        <Login />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("Login hash extraction", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    Object.defineProperty(window, "location", {
      value: { ...window.location, hash: "", pathname: "/login" },
      writable: true,
    });
  });

  it("extracts tokens from hash fragment and navigates", async () => {
    Object.defineProperty(window, "location", {
      value: {
        hash: "#google=success&access_token=tok123&refresh_token=ref456&email=test%40mail.com&name=Test%20User",
        pathname: "/login",
      },
      writable: true,
    });

    renderWithProviders(["/login"]);

    await waitFor(() => {
      expect(localStorage.getItem("access_token")).toBe("tok123");
      expect(localStorage.getItem("refresh_token")).toBe("ref456");
    });
  });

  it("does not call login with empty access_token", async () => {
    Object.defineProperty(window, "location", {
      value: {
        hash: "#google=success&access_token=&refresh_token=ref456&email=test%40mail.com&name=Test",
        pathname: "/login",
      },
      writable: true,
    });

    renderWithProviders(["/login"]);

    await new Promise((r) => setTimeout(r, 100));
    expect(localStorage.getItem("access_token")).toBeNull();
  });

  it("renders the login form", () => {
    renderWithProviders(["/login"]);
    expect(screen.getByText("Mock LoginForm")).toBeInTheDocument();
  });
});
