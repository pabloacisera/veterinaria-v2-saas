export interface RegisterInput {
  name: string;
  surname: string;
  email: string;
  password: string;
  company_name: string;
  cuit: string;
}

export interface RegisterResult {
  id: string;
  email: string;
  name: string;
  message: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface LoginResult {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface ActivateInput {
  email: string;
  code: string;
}
