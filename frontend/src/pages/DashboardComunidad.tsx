import { useState, useCallback } from "react";
import type { PostData } from "@/entities/community";
import { useCompany } from "@/shared/hooks/useCommunity";
import { CreatePostForm } from "@/features/community/CreatePostForm";
import { PostFeed } from "@/features/community/PostFeed";
import { PostDetail } from "@/features/community/PostDetail";

export function DashboardComunidad() {
  const { data: company, isLoading: checkingCompany } = useCompany();
  const [selectedPost, setSelectedPost] = useState<PostData | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);

  const invisible = company?.invisible ?? false;

  const handleCommentClick = useCallback((post: PostData) => {
    setSelectedPost(post);
    setDetailOpen(true);
  }, []);

  if (checkingCompany) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-gray-400">Cargando...</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Comunidad</h1>
        <p className="mt-1 text-gray-500">
          Compartí novedades, tips y conectá con otros colegas
        </p>
      </div>

      {invisible ? (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <span className="text-xl">👁️</span>
            <p className="text-sm text-amber-800 font-medium">
              Tu empresa está configurada como invisible. Podés ver la comunidad pero no publicar ni comentar.
            </p>
          </div>
        </div>
      ) : (
        <CreatePostForm />
      )}

      <PostFeed onCommentClick={handleCommentClick} />

      <PostDetail
        post={selectedPost}
        open={detailOpen}
        onClose={() => setDetailOpen(false)}
      />
    </div>
  );
}

export default DashboardComunidad;
