import { apiGet, apiPost, apiPut, apiDelete } from "@/shared/lib/api";
export type {
  ClientData,
  CreateClientInput,
  UpdateClientInput,
  ClientListParams,
} from "@/entities/client/types";

export function fetchClients(params?: import("@/entities/client/types").ClientListParams) {
  const searchParams = new URLSearchParams();
  if (params?.search) searchParams.set("search", params.search);
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));
  const qs = searchParams.toString();
  return apiGet<import("@/entities/client/types").PaginatedResponse<import("@/entities/client/types").ClientData>>(`/clients${qs ? `?${qs}` : ""}`);
}

export function fetchClient(id: string) {
  return apiGet<import("@/entities/client/types").ClientData>(`/clients/${id}`);
}

export function createClient(data: import("@/entities/client/types").CreateClientInput) {
  return apiPost<import("@/entities/client/types").ClientData>("/clients", data);
}

export function updateClient(id: string, data: import("@/entities/client/types").UpdateClientInput) {
  return apiPut<import("@/entities/client/types").ClientData>(`/clients/${id}`, data);
}

export function deleteClient(id: string) {
  return apiDelete(`/clients/${id}`);
}
