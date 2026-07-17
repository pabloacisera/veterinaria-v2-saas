import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "@/features/community/api";

const KEY = "community";

export function usePosts(page = 1) {
  return useQuery({
    queryKey: [KEY, "posts", page],
    queryFn: () => api.fetchPosts(page),
  });
}

export function usePostDetail(id: string) {
  return useQuery({
    queryKey: [KEY, "posts", id],
    queryFn: () => api.fetchPostDetail(id),
    enabled: !!id,
  });
}

export function useCreatePost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { content: string; image_url?: string }) => api.createPost(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY, "posts"] }),
  });
}

export function useToggleLike() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (postId: string) => api.toggleLike(postId),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY, "posts"] }),
  });
}

export function useDeletePost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (postId: string) => api.deletePost(postId),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY, "posts"] }),
  });
}

export function useComments(postId: string) {
  return useQuery({
    queryKey: [KEY, "posts", postId, "comments"],
    queryFn: () => api.fetchComments(postId),
    enabled: !!postId,
  });
}

export function useCreateComment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ postId, content }: { postId: string; content: string }) =>
      api.createComment(postId, content),
    onSuccess: (_, { postId }) =>
      qc.invalidateQueries({ queryKey: [KEY, "posts", postId, "comments"] }),
  });
}

export function useCompany() {
  return useQuery({
    queryKey: [KEY, "company"],
    queryFn: () => api.fetchCompany(),
  });
}
