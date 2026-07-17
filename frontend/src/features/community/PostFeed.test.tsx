import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { PostFeed } from "./PostFeed";
import * as communityApi from "./api";
import type { PostData } from "@/entities/community";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

function renderWithQC(component: React.ReactNode) {
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
}

vi.mock("./api", () => ({
  fetchPosts: vi.fn(),
  toggleLike: vi.fn(),
}));

function makePost(overrides: Partial<PostData> = {}): PostData {
  const id = overrides.id ?? Math.random().toString(36).slice(2);
  return {
    id,
    company_id: "c1",
    company_name: "Vet " + id,
    contenido: "Post content " + id,
    likes_count: 0,
    comments_count: 0,
    liked_by_me: false,
    created_at: "2025-06-20T14:00:00Z",
    ...overrides,
  };
}

describe("PostFeed", () => {
  afterEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  it("muestra skeleton loading mientras carga", () => {
    vi.mocked(communityApi.fetchPosts).mockReturnValue(new Promise(() => {}));
    renderWithQC(<PostFeed onCommentClick={vi.fn()} />);

    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("muestra mensaje vacío cuando no hay posts", async () => {
    vi.mocked(communityApi.fetchPosts).mockResolvedValue({ items: [], total: 0, page: 1, limit: 20 });
    renderWithQC(<PostFeed onCommentClick={vi.fn()} />);

    expect(await screen.findByText(/no hay publicaciones aún/i)).toBeInTheDocument();
  });

  it("renderiza posts y botón de cargar más", async () => {
    const page1Posts = Array.from({ length: 20 }, (_, i) => makePost({ id: `p${i}` }));
    vi.mocked(communityApi.fetchPosts).mockResolvedValue({ items: page1Posts, total: 30, page: 1, limit: 20 });

    renderWithQC(<PostFeed onCommentClick={vi.fn()} />);

    expect(await screen.findByText("Post content p0")).toBeInTheDocument();
    expect(screen.getByText("Cargar más")).toBeInTheDocument();
  });

  it("carga más posts al hacer click en cargar más", async () => {
    const page1Posts = Array.from({ length: 20 }, (_, i) => makePost({ id: `p${i}` }));
    const page2Posts = Array.from({ length: 10 }, (_, i) => makePost({ id: `p${i + 20}` }));

    vi.mocked(communityApi.fetchPosts)
      .mockResolvedValueOnce({ items: page1Posts, total: 30, page: 1, limit: 20 })
      .mockResolvedValueOnce({ items: page2Posts, total: 30, page: 2, limit: 20 });

    renderWithQC(<PostFeed onCommentClick={vi.fn()} />);

    expect(await screen.findByText("Post content p0")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Cargar más"));

    await waitFor(() => {
      expect(screen.getByText("Post content p29")).toBeInTheDocument();
    });
  });

  it("no muestra cargar más cuando no hay más páginas", async () => {
    const posts = Array.from({ length: 5 }, (_, i) => makePost({ id: `p${i}` }));
    vi.mocked(communityApi.fetchPosts).mockResolvedValue({ items: posts, total: 5, page: 1, limit: 20 });

    renderWithQC(<PostFeed onCommentClick={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText("Post content p0")).toBeInTheDocument();
    });
    expect(screen.queryByText("Cargar más")).not.toBeInTheDocument();
  });
});
