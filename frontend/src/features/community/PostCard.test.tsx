import { render, screen, fireEvent } from "@testing-library/react";
import { vi } from "vitest";
import { PostCard } from "./PostCard";
import type { PostData } from "@/entities/community";

const basePost: PostData = {
  id: "post-1",
  company_id: "c1",
  company_name: "Veterinaria San Martín",
  contenido: "¡Hoy tuvimos 10 consultas!",
  likes_count: 5,
  comments_count: 3,
  liked_by_me: false,
  created_at: "2025-06-20T14:00:00Z",
};

describe("PostCard", () => {
  it("renderiza contenido del post", () => {
    render(<PostCard post={basePost} onLike={vi.fn()} onCommentClick={vi.fn()} />);
    expect(screen.getByText("¡Hoy tuvimos 10 consultas!")).toBeInTheDocument();
    expect(screen.getByText("Veterinaria San Martín")).toBeInTheDocument();
  });

  it("muestra la imagen cuando el post tiene imagen", () => {
    const postConImagen = { ...basePost, imagen_url: "https://example.com/img.jpg" };
    render(<PostCard post={postConImagen} onLike={vi.fn()} onCommentClick={vi.fn()} />);
    const img = screen.getByAltText("Imagen del post");
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute("src", "https://example.com/img.jpg");
  });

  it("no muestra imagen cuando el post no tiene", () => {
    render(<PostCard post={basePost} onLike={vi.fn()} onCommentClick={vi.fn()} />);
    expect(screen.queryByAltText("Imagen del post")).not.toBeInTheDocument();
  });

  it("muestra contadores de likes y comentarios", () => {
    render(<PostCard post={basePost} onLike={vi.fn()} onCommentClick={vi.fn()} />);
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("llama a onLike al hacer click en like", () => {
    const onLike = vi.fn();
    render(<PostCard post={basePost} onLike={onLike} onCommentClick={vi.fn()} />);
    fireEvent.click(screen.getByText("5"));
    expect(onLike).toHaveBeenCalledWith("post-1");
  });

  it("llama a onCommentClick al hacer click en comentarios", () => {
    const onCommentClick = vi.fn();
    render(<PostCard post={basePost} onLike={vi.fn()} onCommentClick={onCommentClick} />);
    fireEvent.click(screen.getByText("3"));
    expect(onCommentClick).toHaveBeenCalledWith(basePost);
  });

  it("muestra corazón lleno cuando liked_by_me es true", () => {
    const likedPost = { ...basePost, liked_by_me: true };
    const { container } = render(<PostCard post={likedPost} onLike={vi.fn()} onCommentClick={vi.fn()} />);
    const hearts = container.querySelectorAll("svg");
    expect(hearts[0].getAttribute("class")).toContain("fill-current");
  });

  it("usa inicial del nombre de la compañía", () => {
    render(<PostCard post={basePost} onLike={vi.fn()} onCommentClick={vi.fn()} />);
    expect(screen.getByText("V")).toBeInTheDocument();
  });
});
