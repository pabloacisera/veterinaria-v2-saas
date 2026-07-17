import { vi } from "vitest";
import { registerUser, loginUser, activateAccount } from "./api";

vi.mock("@/shared/lib/api", () => ({
  apiPost: vi.fn(),
}));

import { apiPost } from "@/shared/lib/api";

describe("auth api", () => {
  afterEach(() => vi.clearAllMocks());

  it("registerUser llama a POST /auth/register", async () => {
    const mockData = { id: "1", email: "test@test.com", name: "Juan", message: "Cuenta creada" };
    vi.mocked(apiPost).mockResolvedValue(mockData);

    const result = await registerUser({
      name: "Juan",
      surname: "Pérez",
      email: "test@test.com",
      password: "123456",
      company_name: "VetTest",
      cuit: "20-12345678-9",
    });

    expect(apiPost).toHaveBeenCalledWith("/auth/register", {
      name: "Juan",
      surname: "Pérez",
      email: "test@test.com",
      password: "123456",
      company_name: "VetTest",
      cuit: "20-12345678-9",
    });
    expect(result).toEqual(mockData);
  });

  it("loginUser llama a POST /auth/login", async () => {
    const mockData = {
      access_token: "abc",
      refresh_token: "xyz",
      token_type: "bearer",
      expires_in: 3600,
    };
    vi.mocked(apiPost).mockResolvedValue(mockData);

    const result = await loginUser({ email: "test@test.com", password: "123456" });

    expect(apiPost).toHaveBeenCalledWith("/auth/login", {
      email: "test@test.com",
      password: "123456",
    });
    expect(result).toEqual(mockData);
  });

  it("activateAccount llama a POST /auth/activate", async () => {
    const mockData = { message: "Cuenta activada exitosamente" };
    vi.mocked(apiPost).mockResolvedValue(mockData);

    const result = await activateAccount({ email: "test@test.com", code: "123456" });

    expect(apiPost).toHaveBeenCalledWith("/auth/activate", {
      email: "test@test.com",
      code: "123456",
    });
    expect(result).toEqual(mockData);
  });
});
