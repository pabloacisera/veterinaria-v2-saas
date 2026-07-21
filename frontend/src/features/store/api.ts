import { apiGet, apiPost, apiDelete } from "@/shared/lib/api";
export type {
  SaleData,
  SaleWithItems,
  SaleItemData,
  SaleItemInput,
  CreateSaleInput,
  SaleListParams,
} from "@/entities/store/types";
import type { DocumentResponse } from "@/entities/document/types";

export function createSale(data: import("@/entities/store/types").CreateSaleInput) {
  return apiPost<import("@/entities/store/types").SaleData>("/stores/sales", data);
}

export function fetchSales(params?: import("@/entities/store/types").SaleListParams) {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));
  const qs = searchParams.toString();
  return apiGet<import("@/entities/store/types").SaleData[]>(`/stores/sales${qs ? `?${qs}` : ""}`);
}

export function fetchSale(id: string) {
  return apiGet<import("@/entities/store/types").SaleWithItems>(`/stores/sales/${id}`);
}

export function saveDraft(step: number, data: Record<string, unknown>) {
  return apiPost(`/stores/draft?step=${step}`, data);
}

export function getDraft() {
  return apiGet<Record<string, unknown> | null>("/stores/draft/current");
}

export function clearDraft() {
  return apiDelete("/stores/draft/current");
}

export function downloadSaleFactura(saleId: string) {
  return apiGet<DocumentResponse>(`/stores/sales/${saleId}/factura`);
}
