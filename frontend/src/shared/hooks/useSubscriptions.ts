import { useQuery, useMutation } from "@tanstack/react-query";
import * as api from "@/features/subscriptions/api";

const KEY = "subscriptions";

export function useSubscriptionStatus() {
  return useQuery({
    queryKey: [KEY, "status"],
    queryFn: () => api.fetchSubscriptionStatus(),
  });
}

export function useInitSubscription() {
  return useMutation({
    mutationFn: (plan: string) => api.initSubscription(plan),
  });
}

export function useOAuthStatus() {
  return useQuery({
    queryKey: [KEY, "oauth"],
    queryFn: () => api.fetchOAuthStatus(),
  });
}
