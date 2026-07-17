import { apiGet, apiPost, apiDelete } from "@/shared/lib/api";
import type {
  PostData,
  PostListResponse,
  CommentData,
  CreatePostInput,
  CreateCommentInput,
} from "@/entities/community";
import type { CompanyData } from "@/entities/company/types";

export function fetchPosts(page: number, limit: number = 20) {
  return apiGet<PostListResponse>(`/community/posts?page=${page}&limit=${limit}`);
}

export function createPost(data: CreatePostInput) {
  return apiPost<PostData>("/community/posts", data);
}

export function fetchPostDetail(id: string) {
  return apiGet<PostData>(`/community/posts/${id}`);
}

export function createComment(postId: string, data: CreateCommentInput) {
  return apiPost<CommentData>(`/community/posts/${postId}/comments`, data);
}

export function toggleLike(postId: string) {
  return apiPost<{ liked: boolean }>(`/community/posts/${postId}/like`, {});
}

export function fetchComments(postId: string) {
  return apiGet<CommentData[]>(`/community/posts/${postId}/comments`);
}

export function deletePost(id: string) {
  return apiDelete(`/community/posts/${id}`);
}

export function fetchCompany() {
  return apiGet<CompanyData>("/company/me");
}
