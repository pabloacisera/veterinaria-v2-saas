export interface CompanyAdmin {
  id: string;
  cuit: string | null;
  nombre: string;
  plan: string | null;
  estado: string | null;
  inicio_suscripcion: string | null;
  fin_suscripcion: string | null;
  requests_usados: number;
}

export interface CompanyListResponse {
  items: CompanyAdmin[];
  total: number;
  page: number;
  page_size: number;
}

export interface AdminActionResponse {
  message: string;
}

export interface BackupLogItem {
  id: string;
  tipo: string;
  estado: string;
  mensaje: string;
  ejecutado_en: string;
}
