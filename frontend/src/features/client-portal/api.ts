import { clientGet } from "./clientApi";

export function fetchMisMascotas() {
  return clientGet<any[]>("/cliente/mis-mascotas");
}

export function fetchFacturas() {
  return clientGet<any[]>("/cliente/facturas");
}

export function fetchPrescripciones() {
  return clientGet<any[]>("/cliente/prescripciones");
}
