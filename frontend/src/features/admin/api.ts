import { adminGet, adminGetBlob, adminPost } from "./adminApi";
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
  return adminGet<CompanyListResponse>(
    `${ADMIN_PREFIX}/companias${qs ? `?${qs}` : ""}`
  );
}

export function blockCompania(id: string) {
  return adminPost<AdminActionResponse>(`${ADMIN_PREFIX}/companias/${id}/bloquear`, {});
}

export function unblockCompania(id: string) {
  return adminPost<AdminActionResponse>(`${ADMIN_PREFIX}/companias/${id}/desbloquear`, {});
}

export function grantFreeSubscription(id: string, dias: number) {
  return adminPost<{ message: string; nueva_fin: string }>(
    `${ADMIN_PREFIX}/companias/${id}/suscripcion-gratuita`,
    { dias }
  );
}

export async function exportCompanias() {
  const blob = await adminGetBlob(`${ADMIN_PREFIX}/exportar/companias`);
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "companias.csv";
  a.click();
  URL.revokeObjectURL(url);
}

export function fetchBackupHistorial() {
  return adminGet<BackupLogItem[]>(`${ADMIN_PREFIX}/backup/historial`);
}

export function triggerBackup() {
  return adminPost<{ status: string }>(`${ADMIN_PREFIX}/backup/manual`, {});
}

export type { CompanyAdmin, CompanyListResponse, AdminActionResponse, BackupLogItem };
