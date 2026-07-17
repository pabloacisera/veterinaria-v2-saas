import { useState } from "react";
import { useCreatePost } from "@/shared/hooks/useCommunity";
import { Button } from "@/shared/ui/Button";
import { Card } from "@/shared/ui/Card";

export function CreatePostForm() {
  const createPostMutation = useCreatePost();
  const [contenido, setContenido] = useState("");
  const [imagenUrl, setImagenUrl] = useState("");
  const [showImageInput, setShowImageInput] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!contenido.trim()) return;
    try {
      await createPostMutation.mutateAsync({
        content: contenido.trim(),
        image_url: imagenUrl.trim() || undefined,
      });
      setContenido("");
      setImagenUrl("");
      setShowImageInput(false);
    } catch {
      // silent
    }
  }

  return (
    <Card className="p-5">
      <form onSubmit={handleSubmit} className="space-y-3">
        <textarea
          placeholder="¿Qué querés compartir con la comunidad?"
          value={contenido}
          onChange={(e) => setContenido(e.target.value)}
          rows={3}
          className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm shadow-sm transition-colors placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
        />

        {showImageInput && (
          <input
            type="text"
            placeholder="URL de la imagen (opcional)"
            value={imagenUrl}
            onChange={(e) => setImagenUrl(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        )}

        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => setShowImageInput(!showImageInput)}
            className="text-sm text-gray-400 hover:text-gray-600 transition-colors flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {showImageInput ? "Quitar imagen" : "Agregar imagen"}
          </button>

          <Button type="submit" disabled={!contenido.trim()} loading={createPostMutation.isPending} size="sm">
            Publicar
          </Button>
        </div>
      </form>
    </Card>
  );
}
