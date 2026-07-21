import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "@/features/cash/api";

const KEY = "cash";

export function useMovements(params?: import("@/entities/cash/types").MovementListParams) {
  const query = useQuery({
    queryKey: [KEY, "movements", params],
    queryFn: () => api.fetchMovements(params),
  });
  return {
    ...query,
    data: query.data?.items ?? [],
    total: query.data?.total ?? 0,
  };
}

export function useMovement(id: string) {
  return useQuery({
    queryKey: [KEY, "movements", id],
    queryFn: () => api.fetchMovement(id),
    enabled: !!id,
  });
}

export function useCreateMovement() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: import("@/entities/cash/types").CreateMovementInput) => api.createMovement(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useUpdateMovementStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => api.updateMovementStatus(id, status),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}
