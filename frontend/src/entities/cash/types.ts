export interface CashMovementData {
  id: string;
  company_id: string;
  movement_type: string;
  category: string | null;
  amount: number;
  description: string | null;
  payment_method: string | null;
  status: string;
  source_type: string | null;
  source_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateMovementInput {
  movement_type: "income" | "expense";
  amount: number;
  category?: string;
  description?: string;
  payment_method?: string;
  status?: "pagado" | "pendiente";
}

export interface MovementListParams {
  status?: string;
  movement_type?: string;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
}
