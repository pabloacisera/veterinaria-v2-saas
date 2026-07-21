import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "@/features/store/api";

const KEY = "store";

export function useSales(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: [KEY, "sales", params],
    queryFn: () => api.fetchSales(params),
  });
}

export function useSale(id: string) {
  return useQuery({
    queryKey: [KEY, "sales", id],
    queryFn: () => api.fetchSale(id),
    enabled: !!id,
  });
}

export function useCreateSale() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: import("@/entities/store/types").CreateSaleInput) => api.createSale(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useSaveDraft() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ step, data }: { step: number; data: unknown }) => api.saveDraft(step, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY, "draft"] }),
  });
}

export function useGetDraft() {
  return useQuery({
    queryKey: [KEY, "draft", "current"],
    queryFn: () => api.getDraft(),
  });
}

export function useClearDraft() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.clearDraft(),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY, "draft"] }),
  });
}
