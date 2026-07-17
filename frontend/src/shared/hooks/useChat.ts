import { useQuery, useQueryClient } from "@tanstack/react-query";
import * as api from "@/features/chat/api";

const KEY = "chat";

export function useCuota() {
  return useQuery({
    queryKey: [KEY, "cuota"],
    queryFn: () => api.fetchCuota(),
  });
}

export function useHistorial() {
  return useQuery({
    queryKey: [KEY, "historial"],
    queryFn: () => api.fetchHistorial(),
  });
}

export function useInvalidateChat() {
  const qc = useQueryClient();
  return () => qc.invalidateQueries({ queryKey: [KEY] });
}
