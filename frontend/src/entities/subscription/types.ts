export interface InitSubscriptionResponse {
  init_point: string;
  preapproval_id: string;
  subscription_id: string;
}

export interface SubscriptionStatusData {
  plan: string;
  status: string;
  start_date: string;
  end_date: string | null;
  next_billing_date: string | null;
}

export interface OAuthStatusData {
  conectado: boolean;
  mp_user_id: string | null;
}

export interface OAuthInitData {
  auth_url: string;
}
