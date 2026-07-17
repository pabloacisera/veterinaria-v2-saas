import { apiGet } from "@/shared/lib/api";

export interface ClientCountResult {
  total: number;
}

export function fetchClientCount() {
  return apiGet<ClientCountResult>("/clients?limit=1&offset=0");
}
