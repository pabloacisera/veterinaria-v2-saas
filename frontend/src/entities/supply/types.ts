export interface SupplyData {
  id: string;
  company_id: string;
  name: string;
  brand: string | null;
  description: string | null;
  unit_base: string;
  unit_price: number;
  stock_quantity: number;
  min_stock: number;
  created_at: string;
  updated_at: string;
}

export interface CreateSupplyInput {
  name: string;
  unit_base: string;
  brand?: string;
  description?: string;
  unit_price?: number;
  stock_quantity?: number;
  min_stock?: number;
}

export interface UpdateSupplyInput {
  name?: string;
  unit_base?: string;
  brand?: string;
  description?: string;
  unit_price?: number;
  stock_quantity?: number;
  min_stock?: number;
}

export interface SupplyListParams {
  search?: string;
  limit?: number;
  offset?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
}

export interface ProcedureData {
  id: string;
  company_id: string;
  name: string;
  description: string | null;
  price: number;
  created_at: string;
  updated_at: string;
}
