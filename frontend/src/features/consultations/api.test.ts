import { vi } from "vitest";
import {
  createConsultation,
  fetchConsultations,
  fetchConsultation,
  addProcedures,
  addSupplies,
  saveConsultationDraft,
  getConsultationDraft,
  clearConsultationDraft,
} from "./api";

vi.mock("@/shared/lib/api", () => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPut: vi.fn(),
  apiDelete: vi.fn(),
}));

import { apiGet, apiPost, apiDelete } from "@/shared/lib/api";

describe("consultations api", () => {
  afterEach(() => vi.clearAllMocks());

  it("createConsultation llama a POST /consultations", async () => {
    vi.mocked(apiPost).mockResolvedValue({ id: "c1", status: "completed" });
    const result = await createConsultation({
      pet_id: "pet-1",
      reason: "Tos seca",
      diagnosis: "Bronquitis",
    });
    expect(apiPost).toHaveBeenCalledWith("/consultations", {
      pet_id: "pet-1",
      reason: "Tos seca",
      diagnosis: "Bronquitis",
    });
    expect(result).toEqual({ id: "c1", status: "completed" });
  });

  it("fetchConsultations llama a GET /consultations", async () => {
    vi.mocked(apiGet).mockResolvedValue([]);
    await fetchConsultations({ pet_id: "pet-1", limit: 10 });
    expect(apiGet).toHaveBeenCalledWith("/consultations?pet_id=pet-1&limit=10");
  });

  it("fetchConsultation llama a GET /consultations/{id}", async () => {
    vi.mocked(apiGet).mockResolvedValue({ consultation: { id: "c1" }, procedures: [], supplies: [] });
    const result = await fetchConsultation("c1");
    expect(apiGet).toHaveBeenCalledWith("/consultations/c1");
    expect(result).toEqual({ consultation: { id: "c1" }, procedures: [], supplies: [] });
  });

  it("addProcedures llama a POST /consultations/{id}/procedures", async () => {
    vi.mocked(apiPost).mockResolvedValue({ status: "ok" });
    await addProcedures("c1", [{ procedure_id: "p1", quantity: 2 }]);
    expect(apiPost).toHaveBeenCalledWith("/consultations/c1/procedures", [
      { procedure_id: "p1", quantity: 2 },
    ]);
  });

  it("addSupplies llama a POST /consultations/{id}/supplies", async () => {
    vi.mocked(apiPost).mockResolvedValue({ status: "ok" });
    await addSupplies("c1", [{ supply_id: "s1", quantity: 3 }]);
    expect(apiPost).toHaveBeenCalledWith("/consultations/c1/supplies", [
      { supply_id: "s1", quantity: 3 },
    ]);
  });

  it("saveConsultationDraft llama a POST /consultations/draft", async () => {
    vi.mocked(apiPost).mockResolvedValue({ status: "ok" });
    await saveConsultationDraft(2, { reason: "Tos" });
    expect(apiPost).toHaveBeenCalledWith("/consultations/draft?step=2", { reason: "Tos" });
  });

  it("getConsultationDraft llama a GET /consultations/draft/current", async () => {
    vi.mocked(apiGet).mockResolvedValue({ step: 1 });
    const result = await getConsultationDraft();
    expect(apiGet).toHaveBeenCalledWith("/consultations/draft/current");
    expect(result).toEqual({ step: 1 });
  });

  it("clearConsultationDraft llama a DELETE /consultations/draft/current", async () => {
    vi.mocked(apiDelete).mockResolvedValue(undefined);
    await clearConsultationDraft();
    expect(apiDelete).toHaveBeenCalledWith("/consultations/draft/current");
  });
});
