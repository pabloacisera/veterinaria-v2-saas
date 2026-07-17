import { useState } from "react";
import { Button } from "@/shared/ui/Button";

interface CommentFormProps {
  onSubmit: (contenido: string) => Promise<void>;
}

export function CommentForm({ onSubmit }: CommentFormProps) {
  const [contenido, setContenido] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!contenido.trim()) return;
    setSubmitting(true);
    try {
      await onSubmit(contenido.trim());
      setContenido("");
    } catch {
      // silent
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        placeholder="Escribí un comentario..."
        value={contenido}
        onChange={(e) => setContenido(e.target.value)}
        className="block flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
      />
      <Button type="submit" size="sm" disabled={!contenido.trim()} loading={submitting}>
        Comentar
      </Button>
    </form>
  );
}
