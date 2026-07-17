import type { PostData } from "@/entities/community";
import { Card } from "@/shared/ui/Card";

interface PostCardProps {
  post: PostData;
  onLike: (postId: string) => void;
  onCommentClick: (post: PostData) => void;
}

export function PostCard({ post, onLike, onCommentClick }: PostCardProps) {
  const formattedDate = new Date(post.created_at).toLocaleDateString("es-AR", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <Card className="p-5 space-y-3">
      <div className="flex items-center justify-between">
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
      </div>

      <p className="text-sm text-gray-700 whitespace-pre-wrap">{post.contenido}</p>

      {post.imagen_url && (
        <img
          src={post.imagen_url}
          alt="Imagen del post"
          className="rounded-xl max-h-64 w-full object-cover"
        />
      )}

      <div className="flex items-center gap-4 pt-2 border-t border-gray-100">
        <button
          onClick={() => onLike(post.id)}
          className={`flex items-center gap-1.5 text-sm font-medium transition-colors ${
            post.liked_by_me
              ? "text-red-500"
              : "text-gray-400 hover:text-red-500"
          }`}
        >
          {post.liked_by_me ? (
            <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>
          ) : (
            <svg className="w-5 h-5 stroke-current fill-none" viewBox="0 0 24 24" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          )}
          {post.likes_count}
        </button>

        <button
          onClick={() => onCommentClick(post)}
          className="flex items-center gap-1.5 text-sm font-medium text-gray-400 hover:text-primary-500 transition-colors"
        >
          <svg className="w-5 h-5 stroke-current fill-none" viewBox="0 0 24 24" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          {post.comments_count}
        </button>
      </div>
    </Card>
  );
}
