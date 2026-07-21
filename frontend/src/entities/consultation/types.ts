export interface ConsultationData {
  id: string;
  company_id: string;
  pet_id: string;
  reason: string;
  diagnosis: string;
  treatment: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CreateConsultationInput {
  pet_id: string;
  reason: string;
  diagnosis: string;
  treatment?: string;
}

export interface ConsultationProcedureData {
  id: string;
  consultation_id: string;
  procedure_id: string;
  procedure_name: string;
  quantity: number;
  unit_price: number;
}

export interface ConsultationSupplyData {
  id: string;
  consultation_id: string;
  supply_id: string;
  supply_name: string;
  quantity: number;
  unit_price: number;
}

export interface ConsultationDetail {
  consultation: ConsultationData;
  procedures: ConsultationProcedureData[];
  supplies: ConsultationSupplyData[];
}

export interface ConsultationListParams {
  pet_id?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
}
