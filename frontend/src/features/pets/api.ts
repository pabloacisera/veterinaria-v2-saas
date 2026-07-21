import { apiGet, apiPost, apiPut, apiDelete } from "@/shared/lib/api";
import type { PaginatedResponse } from "@/shared/types/pagination";
export type {
  PetData,
  CreatePetInput,
  UpdatePetInput,
  PetListParams,
} from "@/entities/pet/types";

export function fetchPets(params?: import("@/entities/pet/types").PetListParams) {
  const searchParams = new URLSearchParams();
  if (params?.search) searchParams.set("search", params.search);
  if (params?.owner_id) searchParams.set("owner_id", params.owner_id);
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));
  const qs = searchParams.toString();
  return apiGet<PaginatedResponse<import("@/entities/pet/types").PetData>>(`/pets${qs ? `?${qs}` : ""}`);
}

export function fetchPet(id: string) {
  return apiGet<import("@/entities/pet/types").PetData>(`/pets/${id}`);
}

export function createPet(data: import("@/entities/pet/types").CreatePetInput) {
  return apiPost<import("@/entities/pet/types").PetData>("/pets", data);
}

export function updatePet(id: string, data: import("@/entities/pet/types").UpdatePetInput) {
  return apiPut<import("@/entities/pet/types").PetData>(`/pets/${id}`, data);
}

export function deletePet(id: string) {
  return apiDelete(`/pets/${id}`);
}
