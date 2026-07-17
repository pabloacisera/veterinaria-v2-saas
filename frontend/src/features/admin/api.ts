import { apiGet, apiGetBlob, apiPost } from "@/shared/lib/api";
import type { CompanyAdmin, CompanyListResponse, AdminActionResponse, BackupLogItem } from "@/entities/admin";

const ADMIN_PREFIX = "/admin/developer";

export function fetchCompanias(filters?: {
  page?: number;
  page_size?: number;
  estado?: string;
  plan?: string;
  search?: string;
}) {
  const params = new URLSearchParams();
  if (filters?.page) params.set("page", String(filters.page));
  if (filters?.page_size) params.set("page_size", String(filters.page_size));
  if (filters?.estado) params.set("estado", filters.estado);
  if (filters?.plan) params.set("plan", filters.plan);
  if (filters?.search) params.set("search", filters.search);
  const qs = params.toString();
  return apiGet<CompanyListResponse>(
    `${ADMIN_PREFIX}/companias${qs ? `?${qs}` : ""}`
  );
}

export function blockCompania(id: string) {
  return apiPost<AdminActionResponse>(`${ADMIN_PREFIX}/companias/${id}/bloquear`, {});
}

export function unblockCompania(id: string) {
  return apiPost<AdminActionResponse>(`${ADMIN_PREFIX}/companias/${id}/desbloquear`, {});
}

export function grantFreeSubscription(id: string, dias: number) {
  return apiPost<{ message: string; nueva_fin: string }>(
    `${ADMIN_PREFIX}/companias/${id}/suscripcion-gratuita`,
    { dias }
  );
}

export async function exportCompanias() {
  const blob = await apiGetBlob(`${ADMIN_PREFIX}/exportar/companias`);
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "companias.csv";
  a.click();
  URL.revokeObjectURL(url);
}

export function fetchBackupHistorial() {
  return apiGet<BackupLogItem[]>(`${ADMIN_PREFIX}/backup/historial`);
}

export function triggerBackup() {
  return apiPost<{ status: string }>(`${ADMIN_PREFIX}/backup/manual`, {});
}
