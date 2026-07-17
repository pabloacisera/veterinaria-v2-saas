import { useState } from "react";
import type { PostData } from "@/entities/community";
import { usePosts, useToggleLike } from "@/shared/hooks/useCommunity";
import { PostCard } from "./PostCard";
import { Button } from "@/shared/ui/Button";

interface PostFeedProps {
  onCommentClick: (post: PostData) => void;
}

export function PostFeed({ onCommentClick }: PostFeedProps) {
  const [page, setPage] = useState(1);
  const { data, isLoading, isFetching } = usePosts(page);
  const toggleLikeMutation = useToggleLike();

  const posts = data?.items ?? [];
  const total = data?.total ?? 0;
  const hasMore = posts.length < total;

  async function handleLike(postId: string) {
    try {
      await toggleLikeMutation.mutateAsync(postId);
    } catch {
      // silent
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white rounded-2xl border border-gray-100 p-5 space-y-3 animate-pulse">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gray-200" />
              <div className="space-y-1.5 flex-1">
                <div className="h-3 w-24 bg-gray-200 rounded" />
                <div className="h-2.5 w-16 bg-gray-200 rounded" />
              </div>
            </div>
            <div className="space-y-2">
              <div className="h-3 w-full bg-gray-200 rounded" />
              <div className="h-3 w-3/4 bg-gray-200 rounded" />
            </div>
            <div className="h-10 w-full bg-gray-200 rounded-xl" />
            <div className="flex gap-4">
              <div className="h-5 w-12 bg-gray-200 rounded" />
              <div className="h-5 w-12 bg-gray-200 rounded" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (posts.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-gray-100 p-10 text-center">
        <p className="text-4xl mb-3">📝</p>
        <p className="text-gray-500 font-medium">No hay publicaciones aún</p>
        <p className="text-sm text-gray-400 mt-1">
          Sé el primero en compartir algo con la comunidad.
        </p>
      </div>
    );
  }

  function loadMore() {
    setPage((p) => p + 1);
  }

  return (
    <div className="space-y-4">
      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={post}
          onLike={handleLike}
          onCommentClick={onCommentClick}
        />
      ))}

      {hasMore && (
        <div className="flex justify-center pt-2">
          <Button
            variant="outline"
            onClick={loadMore}
            loading={isFetching}
          >
            Cargar más
          </Button>
        </div>
      )}
    </div>
  );
}
