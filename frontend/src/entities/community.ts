export interface PostData {
  id: string;
  company_id: string;
  company_name?: string;
  contenido: string;
  imagen_url?: string;
  likes_count: number;
  comments_count: number;
  liked_by_me: boolean;
  created_at: string;
}

export interface CommentData {
  id: string;
  post_id: string;
  company_id: string;
  company_name?: string;
  contenido: string;
  created_at: string;
}

export interface CreatePostInput {
  contenido: string;
  imagen_url?: string;
}

export interface CreateCommentInput {
  contenido: string;
}

export interface PostListResponse {
  items: PostData[];
  total: number;
  page: number;
  limit: number;
}
