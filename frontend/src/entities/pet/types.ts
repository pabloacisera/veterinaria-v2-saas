export interface PetData {
  id: string;
  company_id: string;
  owner_id: string | null;
  name: string | null;
  species: string | null;
  breed: string | null;
  sex: string;
  birth_date: string | null;
  weight_kg: number | null;
  color: string | null;
  observations: string | null;
  photo_urls: string[];
  created_at: string;
  updated_at: string;
}

export interface CreatePetInput {
  owner_id?: string;
  name?: string;
  species?: string;
  breed?: string;
  sex: string;
  birth_date?: string;
  weight_kg?: number;
  color?: string;
  observations?: string;
}

export interface UpdatePetInput {
  owner_id?: string;
  name?: string;
  species?: string;
  breed?: string;
  sex?: string;
  birth_date?: string;
  weight_kg?: number;
  color?: string;
  observations?: string;
}

export interface PetListParams {
  search?: string;
  owner_id?: string;
  limit?: number;
  offset?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
}
