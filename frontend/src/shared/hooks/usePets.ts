import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "@/features/pets/api";

const KEY = "pets";

export function usePets(params?: import("@/entities/pet/types").PetListParams) {
  return useQuery({
    queryKey: [KEY, params],
    queryFn: () => api.fetchPets(params),
  });
}

export function usePet(id: string) {
  return useQuery({
    queryKey: [KEY, id],
    queryFn: () => api.fetchPet(id),
    enabled: !!id,
  });
}

export function useCreatePet() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: import("@/entities/pet/types").CreatePetInput) => api.createPet(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useUpdatePet() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: import("@/entities/pet/types").UpdatePetInput }) =>
      api.updatePet(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useDeletePet() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deletePet(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}
