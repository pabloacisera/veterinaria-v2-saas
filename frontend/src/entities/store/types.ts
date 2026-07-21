export interface SaleData {
  id: string;
  company_id: string;
  client_id: string | null;
  client_name: string | null;
  status: string;
  payment_method: string;
  subtotal: number;
  iva_amount: number;
  total: number;
  iva_enabled: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface SaleItemData {
  id: string;
  sale_id: string;
  supply_id: string;
  supply_name: string;
  quantity: number;
  unit_price: number;
}

export interface SaleWithItems {
  sale: SaleData;
  items: SaleItemData[];
}

export interface SaleItemInput {
  supply_id: string;
  quantity: number;
  unit_price?: number;
}

export interface CreateSaleInput {
  items: SaleItemInput[];
  client_id?: string;
  client_name?: string;
  payment_method: string;
  status?: string;
  notes?: string;
}

export interface SaleListParams {
  search?: string;
  limit?: number;
  offset?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
}
