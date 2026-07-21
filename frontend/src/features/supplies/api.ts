import { apiGet, apiPost, apiPut, apiDelete } from "@/shared/lib/api";
export type {
  SupplyData,
  CreateSupplyInput,
  UpdateSupplyInput,
  SupplyListParams,
  ProcedureData,
} from "@/entities/supply/types";

export function fetchSupplies(params?: import("@/entities/supply/types").SupplyListParams) {
  const searchParams = new URLSearchParams();
  if (params?.search) searchParams.set("search", params.search);
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));
  const qs = searchParams.toString();
  return apiGet<import("@/entities/supply/types").SupplyData[]>(`/supplies${qs ? `?${qs}` : ""}`);
}

export function fetchSupply(id: string) {
  return apiGet<import("@/entities/supply/types").SupplyData>(`/supplies/${id}`);
}

export function createSupply(data: import("@/entities/supply/types").CreateSupplyInput) {
  return apiPost<import("@/entities/supply/types").SupplyData>("/supplies", data);
}

export function updateSupply(id: string, data: import("@/entities/supply/types").UpdateSupplyInput) {
  return apiPut<import("@/entities/supply/types").SupplyData>(`/supplies/${id}`, data);
}

export function deleteSupply(id: string) {
  return apiDelete(`/supplies/${id}`);
}

export function fetchProcedures(limit = 100, offset = 0) {
  return apiGet<import("@/entities/supply/types").ProcedureData[]>(`/procedures?limit=${limit}&offset=${offset}`);
}
