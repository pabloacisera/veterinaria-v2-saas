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

export interface UploadResult {
  created: number;
  errors: { fila: number; error: string }[];
}

export async function uploadSuppliesCsv(file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", file);
  return apiPost<UploadResult>("/supplies/upload", formData);
}

export function downloadTemplate() {
  const header = "Nombre,Marca,Descripcion,Precio Unitario,Unidad Base,Stock Inicial,Stock Minimo\n";
  const example = "Vacuna Antirrábica,Zoetis,Vacuna antirrábica canina,2500,dosis,50,10\n";
  const blob = new Blob([header + example], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "plantilla_insumos.csv";
  a.click();
  URL.revokeObjectURL(url);
}
