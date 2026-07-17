import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { CreatePostForm } from "./CreatePostForm";
import * as communityApi from "./api";

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
  createPost: vi.fn(),
}));

describe("CreatePostForm", () => {
  afterEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  it("renderiza textarea y botón publicar", () => {
    renderWithQC(<CreatePostForm />);
    expect(
      screen.getByPlaceholderText(/¿qué querés compartir/i)
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /publicar/i })).toBeInTheDocument();
  });

  it("botón publicar deshabilitado si no hay contenido", () => {
    renderWithQC(<CreatePostForm />);
    expect(screen.getByRole("button", { name: /publicar/i })).toBeDisabled();
  });

  it("no muestra input de imagen inicialmente", () => {
    renderWithQC(<CreatePostForm />);
    expect(screen.queryByPlaceholderText(/url de la imagen/i)).not.toBeInTheDocument();
  });

  it("muestra input de imagen al hacer click en Agregar imagen", () => {
    renderWithQC(<CreatePostForm />);
    fireEvent.click(screen.getByText(/agregar imagen/i));
    expect(screen.getByPlaceholderText(/url de la imagen/i)).toBeInTheDocument();
  });

  it("llama a createPost al enviar", async () => {
    vi.mocked(communityApi.createPost).mockResolvedValue({
      id: "new-1",
      company_id: "c1",
      contenido: "Hola comunidad!",
      likes_count: 0,
      comments_count: 0,
      liked_by_me: false,
      created_at: new Date().toISOString(),
    });

    renderWithQC(<CreatePostForm />);

    const textarea = screen.getByPlaceholderText(/¿qué querés compartir/i);
    fireEvent.change(textarea, { target: { value: "Hola comunidad!" } });

    fireEvent.click(screen.getByRole("button", { name: /publicar/i }));

    await waitFor(() => {
      expect(communityApi.createPost).toHaveBeenCalledWith({
        content: "Hola comunidad!",
      });
    });
  });

  it("envía imagen_url cuando se proporciona", async () => {
    vi.mocked(communityApi.createPost).mockResolvedValue({
      id: "new-2",
      company_id: "c1",
      contenido: "Post con imagen",
      imagen_url: "https://example.com/img.jpg",
      likes_count: 0,
      comments_count: 0,
      liked_by_me: false,
      created_at: new Date().toISOString(),
    });

    renderWithQC(<CreatePostForm />);

    const textarea = screen.getByPlaceholderText(/¿qué querés compartir/i);
    fireEvent.change(textarea, { target: { value: "Post con imagen" } });

    fireEvent.click(screen.getByText(/agregar imagen/i));
    const imgInput = screen.getByPlaceholderText(/url de la imagen/i);
    fireEvent.change(imgInput, { target: { value: "https://example.com/img.jpg" } });

    fireEvent.click(screen.getByRole("button", { name: /publicar/i }));

    await waitFor(() => {
      expect(communityApi.createPost).toHaveBeenCalledWith({
        content: "Post con imagen",
        image_url: "https://example.com/img.jpg",
      });
    });
  });

  it("limpia el formulario después de publicar", async () => {
    vi.mocked(communityApi.createPost).mockResolvedValue({
      id: "new-3",
      company_id: "c1",
      contenido: "Test cleanup",
      likes_count: 0,
      comments_count: 0,
      liked_by_me: false,
      created_at: new Date().toISOString(),
    });

    renderWithQC(<CreatePostForm />);

    const textarea = screen.getByPlaceholderText(/¿qué querés compartir/i);
    fireEvent.change(textarea, { target: { value: "Test cleanup" } });
    fireEvent.click(screen.getByText(/agregar imagen/i));
    fireEvent.change(screen.getByPlaceholderText(/url de la imagen/i), {
      target: { value: "https://example.com/img.jpg" },
    });

    fireEvent.click(screen.getByRole("button", { name: /publicar/i }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /publicar/i })).toBeDisabled();
    });
  });
});
