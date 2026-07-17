import { apiGet } from "@/shared/lib/api";

export function fetchMisMascotas() {
  return apiGet<any[]>("/cliente/mis-mascotas");
}

export function fetchFacturas() {
  return apiGet<any[]>("/cliente/facturas");
}

export function fetchPrescripciones() {
  return apiGet<any[]>("/cliente/prescripciones");
}
