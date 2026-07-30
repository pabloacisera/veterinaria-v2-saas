import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "@/features/admin/api";

const KEY = "admin";

export function useCompanias(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: [KEY, "companias", page, pageSize],
    queryFn: () => api.fetchCompanias({ page, page_size: pageSize }),
  });
}

export function useBlockCompania() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (companyId: string) => api.blockCompania(companyId),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY, "companias"] }),
  });
}

export function useUnblockCompania() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (companyId: string) => api.unblockCompania(companyId),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY, "companias"] }),
  });
}

export function useGrantFreeSubscription() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ companyId, dias }: { companyId: string; dias: number }) =>
      api.grantFreeSubscription(companyId, dias),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY, "companias"] }),
  });
}

export function useBackupHistorial() {
  return useQuery({
    queryKey: [KEY, "backups"],
    queryFn: () => api.fetchBackupHistorial(),
  });
}

export function useTriggerBackup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.triggerBackup(),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY, "backups"] }),
  });
}
