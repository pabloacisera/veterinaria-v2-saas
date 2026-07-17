import { apiGet, apiPost } from "@/shared/lib/api";
export type {
  InitSubscriptionResponse,
  SubscriptionStatusData,
  OAuthStatusData,
  OAuthInitData,
} from "@/entities/subscription/types";

export function initSubscription(plan: string) {
  return apiPost<import("@/entities/subscription/types").InitSubscriptionResponse>("/suscripciones/iniciar", { plan });
}

export function fetchSubscriptionStatus() {
  return apiGet<import("@/entities/subscription/types").SubscriptionStatusData>("/suscripciones/estado");
}

export function fetchOAuthStatus() {
  return apiGet<import("@/entities/subscription/types").OAuthStatusData>("/mercadopago/oauth/estado");
}

export function initOAuth() {
  return apiGet<import("@/entities/subscription/types").OAuthInitData>("/mercadopago/oauth/iniciar");
}
