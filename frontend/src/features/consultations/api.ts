import { apiGet, apiPost, apiDelete } from "@/shared/lib/api";
import type { PaginatedResponse } from "@/shared/types/pagination";
export type {
  ConsultationData,
  CreateConsultationInput,
  ConsultationDetail,
  ConsultationProcedureData,
  ConsultationSupplyData,
  ConsultationListParams,
  DocumentResponse,
} from "@/entities/consultation/types";
import type { DocumentResponse } from "@/entities/document/types";

export function createConsultation(data: import("@/entities/consultation/types").CreateConsultationInput) {
  return apiPost<import("@/entities/consultation/types").ConsultationData>("/consultations", data);
}

export function fetchConsultations(params?: import("@/entities/consultation/types").ConsultationListParams) {
  const searchParams = new URLSearchParams();
  if (params?.pet_id) searchParams.set("pet_id", params.pet_id);
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));
  const qs = searchParams.toString();
  return apiGet<PaginatedResponse<import("@/entities/consultation/types").ConsultationData>>(`/consultations${qs ? `?${qs}` : ""}`);
}

export function fetchConsultation(id: string) {
  return apiGet<import("@/entities/consultation/types").ConsultationDetail>(`/consultations/${id}`);
}

export function addProcedures(
  consultationId: string,
  procedures: { procedure_id: string; quantity?: number }[]
) {
  return apiPost(`/consultations/${consultationId}/procedures`, procedures);
}

export function addSupplies(
  consultationId: string,
  supplies: { supply_id: string; quantity?: number }[]
) {
  return apiPost(`/consultations/${consultationId}/supplies`, supplies);
}

export function saveConsultationDraft(step: number, data: Record<string, unknown>) {
  return apiPost(`/consultations/draft?step=${step}`, data);
}

export function getConsultationDraft() {
  return apiGet<Record<string, unknown> | null>("/consultations/draft/current");
}

export function clearConsultationDraft() {
  return apiDelete("/consultations/draft/current");
}

export function downloadFactura(consultationId: string) {
  return apiGet<DocumentResponse>(`/consultations/${consultationId}/factura`);
}

export function downloadPrescripcion(consultationId: string) {
  return apiGet<DocumentResponse>(`/consultations/${consultationId}/prescripcion`);
}
