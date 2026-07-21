export interface ClientData {
  id: string;
  company_id: string;
  name: string;
  surname: string;
  doc_type: string | null;
  doc_number: string | null;
  email: string;
  phone: string | null;
  address: string | null;
  city: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateClientInput {
  name: string;
  surname: string;
  doc_type: string;
  doc_number: string;
  email: string;
  phone?: string;
  address?: string;
  city?: string;
}

export interface UpdateClientInput {
  name?: string;
  surname?: string;
  doc_type?: string;
  doc_number?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
}

export interface ClientListParams {
  search?: string;
  limit?: number;
  offset?: number;
}
