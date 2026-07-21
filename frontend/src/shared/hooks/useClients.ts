import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "@/features/clients/api";

const KEY = "clients";

export function useClients(params?: import("@/entities/client/types").ClientListParams) {
  const query = useQuery({
    queryKey: [KEY, params],
    queryFn: () => api.fetchClients(params),
  });
  return {
    ...query,
    data: query.data?.items ?? [],
    total: query.data?.total ?? 0,
  };
}

export function useClient(id: string) {
  return useQuery({
    queryKey: [KEY, id],
    queryFn: () => api.fetchClient(id),
    enabled: !!id,
  });
}

export function useCreateClient() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: import("@/entities/client/types").CreateClientInput) => api.createClient(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useUpdateClient() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: import("@/entities/client/types").UpdateClientInput }) =>
      api.updateClient(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useDeleteClient() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteClient(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}
