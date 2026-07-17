export interface CompanyData {
  id: string;
  name: string;
  cuit: string | null;
  professional_name: string | null;
  professional_license: string | null;
  address: string | null;
  website: string | null;
  phone: string | null;
  email: string | null;
  iva_enabled: boolean;
  rag_activated: boolean;
  llm_provider: string;
  llm_model: string;
  invisible: boolean;
  created_at: string;
  updated_at: string;
}
