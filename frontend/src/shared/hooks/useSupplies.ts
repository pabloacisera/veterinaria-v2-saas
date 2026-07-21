import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "@/features/supplies/api";

const KEY = "supplies";

export function useSupplies(params?: import("@/entities/supply/types").SupplyListParams) {
  const query = useQuery({
    queryKey: [KEY, params],
    queryFn: () => api.fetchSupplies(params),
  });
  return {
    ...query,
    data: query.data?.items ?? [],
    total: query.data?.total ?? 0,
  };
}

export function useSupply(id: string) {
  return useQuery({
    queryKey: [KEY, id],
    queryFn: () => api.fetchSupply(id),
    enabled: !!id,
  });
}

export function useCreateSupply() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: import("@/entities/supply/types").CreateSupplyInput) => api.createSupply(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useUpdateSupply() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: import("@/entities/supply/types").UpdateSupplyInput }) =>
      api.updateSupply(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useDeleteSupply() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteSupply(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useProcedures(limit = 100, offset = 0) {
  const query = useQuery({
    queryKey: ["procedures", limit, offset],
    queryFn: () => api.fetchProcedures(limit, offset),
  });
  return {
    ...query,
    data: query.data?.items ?? [],
    total: query.data?.total ?? 0,
  };
}
