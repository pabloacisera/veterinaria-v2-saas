import { vi } from "vitest";
import { fetchPets, fetchPet, createPet, updatePet, deletePet } from "./api";

vi.mock("@/shared/lib/api", () => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPut: vi.fn(),
  apiDelete: vi.fn(),
}));

import { apiGet, apiPost, apiPut, apiDelete } from "@/shared/lib/api";

describe("pets api", () => {
  afterEach(() => vi.clearAllMocks());

  it("fetchPets llama a GET /pets con owner_id", async () => {
    vi.mocked(apiGet).mockResolvedValue([]);
    await fetchPets({ owner_id: "owner-1", limit: 20 });
    expect(apiGet).toHaveBeenCalledWith("/pets?owner_id=owner-1&limit=20");
  });

  it("fetchPet llama a GET /pets/{id}", async () => {
    vi.mocked(apiGet).mockResolvedValue({ id: "pet-1", name: "Luna" });
    const result = await fetchPet("pet-1");
    expect(apiGet).toHaveBeenCalledWith("/pets/pet-1");
    expect(result).toEqual({ id: "pet-1", name: "Luna" });
  });

  it("createPet llama a POST /pets", async () => {
    vi.mocked(apiPost).mockResolvedValue({ id: "pet-1" });
    await createPet({ sex: "Macho", name: "Luna", species: "Perro" });
    expect(apiPost).toHaveBeenCalledWith("/pets", {
      sex: "Macho",
      name: "Luna",
      species: "Perro",
    });
  });

  it("updatePet llama a PUT /pets/{id}", async () => {
    vi.mocked(apiPut).mockResolvedValue({ id: "pet-1" });
    await updatePet("pet-1", { name: "Nueva Luna" });
    expect(apiPut).toHaveBeenCalledWith("/pets/pet-1", { name: "Nueva Luna" });
  });

  it("deletePet llama a DELETE /pets/{id}", async () => {
    vi.mocked(apiDelete).mockResolvedValue(undefined);
    await deletePet("pet-1");
    expect(apiDelete).toHaveBeenCalledWith("/pets/pet-1");
  });
});
