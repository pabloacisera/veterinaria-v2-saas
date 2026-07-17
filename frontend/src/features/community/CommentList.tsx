import type { CommentData } from "@/entities/community";

interface CommentListProps {
  comments: CommentData[];
  loading: boolean;
}

export function CommentList({ comments, loading }: CommentListProps) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2].map((i) => (
          <div key={i} className="animate-pulse flex gap-2">
            <div className="w-6 h-6 rounded-full bg-gray-200 shrink-0" />
            <div className="flex-1 space-y-1.5">
              <div className="h-2.5 w-20 bg-gray-200 rounded" />
              <div className="h-3 w-full bg-gray-200 rounded" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (comments.length === 0) {
    return (
      <p className="text-sm text-gray-400 text-center py-4">
        No hay comentarios aún. ¡Sé el primero en comentar!
      </p>
    );
  }

  return (
    <div className="space-y-3 max-h-64 overflow-y-auto">
      {comments.map((comment) => (
        <div key={comment.id} className="flex gap-2">
          <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-xs font-bold text-gray-500 shrink-0 mt-0.5">
            {(comment.company_name || "U").charAt(0).toUpperCase()}
          </div>
          <div>
            <div className="flex items-baseline gap-2">
              <span className="text-xs font-semibold text-gray-900">
                {comment.company_name || "Usuario"}
              </span>
              <span className="text-[10px] text-gray-400">
                {new Date(comment.created_at).toLocaleDateString("es-AR", {
                  day: "numeric",
                  month: "short",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
            <p className="text-sm text-gray-700">{comment.contenido}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
