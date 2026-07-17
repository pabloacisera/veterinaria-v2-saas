import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "@/features/consultations/api";

const KEY = "consultations";

export function useConsultations(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: [KEY, params],
    queryFn: () => api.fetchConsultations(params),
  });
}

export function useConsultation(id: string) {
  return useQuery({
    queryKey: [KEY, id],
    queryFn: () => api.fetchConsultation(id),
    enabled: !!id,
  });
}

export function useCreateConsultation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: import("@/entities/consultation/types").CreateConsultationInput) =>
      api.createConsultation(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}
