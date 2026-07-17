import type { PostData } from "@/entities/community";
import { useComments, useCreateComment } from "@/shared/hooks/useCommunity";
import { Modal } from "@/shared/ui/Modal";
import { CommentList } from "./CommentList";
import { CommentForm } from "./CommentForm";

interface PostDetailProps {
  post: PostData | null;
  open: boolean;
  onClose: () => void;
}

export function PostDetail({ post, open, onClose }: PostDetailProps) {
  const { data: comments = [], isLoading: loadingComments } = useComments(post?.id ?? "");
  const createCommentMutation = useCreateComment();

  if (!post) return null;

  async function handleComment(contenido: string) {
    try {
      await createCommentMutation.mutateAsync({ postId: post.id, content: contenido });
    } catch {
      // silent
    }
  }

  const formattedDate = new Date(post.created_at).toLocaleDateString("es-AR", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <Modal open={open} onClose={onClose} title="Publicación">
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-sm font-bold text-primary-600">
            {(post.company_name || "U").charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900">
              {post.company_name || "Usuario"}
            </p>
            <p className="text-xs text-gray-400">{formattedDate}</p>
          </div>
        </div>

        <p className="text-sm text-gray-700 whitespace-pre-wrap">{post.contenido}</p>

        {post.imagen_url && (
          <img
            src={post.imagen_url}
            alt="Imagen del post"
            className="rounded-xl max-h-64 w-full object-cover"
          />
        )}

        <div className="flex items-center gap-1 text-sm text-gray-400 pb-2 border-b border-gray-100">
          <span>{post.likes_count} me gusta</span>
          <span className="mx-1">·</span>
          <span>{post.comments_count} comentarios</span>
        </div>

        <CommentList comments={comments} loading={loadingComments} />

        <CommentForm onSubmit={handleComment} />
      </div>
    </Modal>
  );
}
