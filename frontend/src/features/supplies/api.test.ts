import { vi } from "vitest";
import {
  fetchSupplies,
  fetchSupply,
  createSupply,
  updateSupply,
  deleteSupply,
  fetchProcedures,
} from "./api";

vi.mock("@/shared/lib/api", () => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPut: vi.fn(),
  apiDelete: vi.fn(),
}));

import { apiGet, apiPost, apiPut, apiDelete } from "@/shared/lib/api";

describe("supplies api", () => {
  afterEach(() => vi.clearAllMocks());

  it("fetchSupplies llama a GET /supplies con search", async () => {
    vi.mocked(apiGet).mockResolvedValue([]);
    await fetchSupplies({ search: "amox" });
    expect(apiGet).toHaveBeenCalledWith("/supplies?search=amox");
  });

  it("fetchSupply llama a GET /supplies/{id}", async () => {
    vi.mocked(apiGet).mockResolvedValue({ id: "s1", name: "Amoxicilina" });
    const result = await fetchSupply("s1");
    expect(apiGet).toHaveBeenCalledWith("/supplies/s1");
    expect(result).toEqual({ id: "s1", name: "Amoxicilina" });
  });

  it("createSupply llama a POST /supplies", async () => {
    vi.mocked(apiPost).mockResolvedValue({ id: "s1" });
    await createSupply({ name: "Amoxicilina", unit_base: "pastilla", unit_price: 150 });
    expect(apiPost).toHaveBeenCalledWith("/supplies", {
      name: "Amoxicilina",
      unit_base: "pastilla",
      unit_price: 150,
    });
  });

  it("updateSupply llama a PUT /supplies/{id}", async () => {
    vi.mocked(apiPut).mockResolvedValue({ id: "s1" });
    await updateSupply("s1", { unit_price: 200 });
    expect(apiPut).toHaveBeenCalledWith("/supplies/s1", { unit_price: 200 });
  });

  it("deleteSupply llama a DELETE /supplies/{id}", async () => {
    vi.mocked(apiDelete).mockResolvedValue(undefined);
    await deleteSupply("s1");
    expect(apiDelete).toHaveBeenCalledWith("/supplies/s1");
  });

  it("fetchProcedures llama a GET /procedures", async () => {
    vi.mocked(apiGet).mockResolvedValue([{ id: "p1", name: "Vacunación" }]);
    const result = await fetchProcedures(50, 0);
    expect(apiGet).toHaveBeenCalledWith("/procedures?limit=50&offset=0");
    expect(result).toEqual([{ id: "p1", name: "Vacunación" }]);
  });
});
