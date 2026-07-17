import { vi } from "vitest";
import { fetchClients, fetchClient, createClient, updateClient, deleteClient } from "./api";

vi.mock("@/shared/lib/api", () => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPut: vi.fn(),
  apiDelete: vi.fn(),
}));

import { apiGet, apiPost, apiPut, apiDelete } from "@/shared/lib/api";

describe("clients api", () => {
  afterEach(() => vi.clearAllMocks());

  it("fetchClients llama a GET /clients con parámetros", async () => {
    vi.mocked(apiGet).mockResolvedValue([]);
    await fetchClients({ search: "Juan", limit: 10 });
    expect(apiGet).toHaveBeenCalledWith("/clients?search=Juan&limit=10");
  });

  it("fetchClient llama a GET /clients/{id}", async () => {
    const mockClient = { id: "1", name: "Juan" };
    vi.mocked(apiGet).mockResolvedValue(mockClient);
    const result = await fetchClient("1");
    expect(apiGet).toHaveBeenCalledWith("/clients/1");
    expect(result).toEqual(mockClient);
  });

  it("createClient llama a POST /clients", async () => {
    const mockClient = { id: "1", name: "Juan", email: "test@test.com" };
    vi.mocked(apiPost).mockResolvedValue(mockClient);
    const result = await createClient({
      name: "Juan",
      surname: "Pérez",
      email: "test@test.com",
      doc_type: "DNI",
      doc_number: "12345678",
    });
    expect(apiPost).toHaveBeenCalledWith("/clients", {
      name: "Juan",
      surname: "Pérez",
      email: "test@test.com",
      doc_type: "DNI",
      doc_number: "12345678",
    });
    expect(result).toEqual(mockClient);
  });

  it("updateClient llama a PUT /clients/{id}", async () => {
    vi.mocked(apiPut).mockResolvedValue({ id: "1" });
    await updateClient("1", { name: "Nuevo nombre" });
    expect(apiPut).toHaveBeenCalledWith("/clients/1", { name: "Nuevo nombre" });
  });

  it("deleteClient llama a DELETE /clients/{id}", async () => {
    vi.mocked(apiDelete).mockResolvedValue(undefined);
    await deleteClient("1");
    expect(apiDelete).toHaveBeenCalledWith("/clients/1");
  });
});
