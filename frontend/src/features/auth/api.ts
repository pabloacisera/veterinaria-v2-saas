import { apiGet, apiPost } from "@/shared/lib/api";
export type {
  RegisterInput,
  RegisterResult,
  LoginInput,
  LoginResult,
  ActivateInput,
} from "@/entities/auth/types";

export function registerUser(data: import("@/entities/auth/types").RegisterInput) {
  return apiPost<import("@/entities/auth/types").RegisterResult>("/auth/register", data);
}

export function loginUser(data: import("@/entities/auth/types").LoginInput) {
  return apiPost<import("@/entities/auth/types").LoginResult>("/auth/login", data);
}

export function activateAccount(data: import("@/entities/auth/types").ActivateInput) {
  return apiPost<{ message: string }>("/auth/activate", data);
}

export function fetchCurrentUser() {
  return apiGet<{ email: string; name: string; company_id: string }>("/auth/me");
}

export function logoutUser() {
  return apiPost<{ message: string }>("/auth/logout", {});
}
