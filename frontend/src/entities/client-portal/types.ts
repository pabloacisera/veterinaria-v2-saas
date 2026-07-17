export interface AccesoResponse {
  access_token: string;
  token_type: string;
}

export interface MascotaCliente {
  id: string;
  nombre: string;
  raza: string;
  sexo: string;
  edad?: number;
  foto_url?: string;
}

export interface FacturaCliente {
  id: string;
  tipo: string;
  monto: number;
  estado: "pagado" | "pendiente";
  fecha: string;
  descargar_url?: string;
  qr_data?: string;
  alias?: string;
  cbu?: string;
}

export interface PrescripcionCliente {
  id: string;
  mascota_nombre: string;
  fecha: string;
  descargar_url: string;
}

export interface PendingPayment {
  amount: number;
  payment_method: string;
  status: string;
}

export interface Factura {
  id: string;
  entity_type: string;
  entity_id: string;
  download_url: string | null;
  version: number;
  created_at: string;
  pending_payment?: PendingPayment;
}

export interface Prescripcion {
  id: string;
  entity_id: string;
  download_url: string | null;
  version: number;
  created_at: string;
}
