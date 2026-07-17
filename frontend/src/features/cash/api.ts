import { apiGet, apiPost, apiPatch } from "@/shared/lib/api";
export type {
  CashMovementData,
  CreateMovementInput,
  MovementListParams,
} from "@/entities/cash/types";

export function fetchMovements(params?: import("@/entities/cash/types").MovementListParams) {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set("status", params.status);
  if (params?.movement_type) searchParams.set("movement_type", params.movement_type);
  if (params?.date_from) searchParams.set("date_from", params.date_from);
  if (params?.date_to) searchParams.set("date_to", params.date_to);
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));
  const qs = searchParams.toString();
  return apiGet<import("@/entities/cash/types").CashMovementData[]>(`/cash/movements${qs ? `?${qs}` : ""}`);
}

export function fetchMovement(id: string) {
  return apiGet<import("@/entities/cash/types").CashMovementData>(`/cash/movements/${id}`);
}

export function createMovement(data: import("@/entities/cash/types").CreateMovementInput) {
  return apiPost<import("@/entities/cash/types").CashMovementData>("/cash/movements", data);
}

export function updateMovementStatus(id: string, status: string) {
  return apiPatch<import("@/entities/cash/types").CashMovementData>(`/cash/movements/${id}/status`, { status });
}
