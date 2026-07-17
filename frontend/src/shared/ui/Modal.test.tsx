import { render, screen, fireEvent } from "@testing-library/react";
import { Modal } from "./Modal";

describe("Modal", () => {
  it("no renderiza nada cuando open=false", () => {
    render(<Modal open={false} onClose={vi.fn()} title="Test" />);
    expect(screen.queryByText(/test/i)).not.toBeInTheDocument();
  });

  it("renderiza el modal cuando open=true", () => {
    render(<Modal open={true} onClose={vi.fn()} title="Título del modal" />);
    expect(screen.getByText(/título del modal/i)).toBeInTheDocument();
    const modalContent = screen.getByText(/título del modal/i).closest("div.relative");
    expect(modalContent).toBeInTheDocument();
  });

  it("renderiza los children", () => {
    render(
      <Modal open={true} onClose={vi.fn()} title="Test">
        <p>Contenido del modal</p>
      </Modal>
    );
    expect(screen.getByText(/contenido del modal/i)).toBeInTheDocument();
  });

  it("cierra al hacer click en overlay", () => {
    const onClose = vi.fn();
    render(<Modal open={true} onClose={onClose} title="Test" />);
    const overlay = document.querySelector(".fixed.inset-0.bg-black\\/40");
    fireEvent.click(overlay!);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("cierra al hacer click en botón de cerrar", () => {
    const onClose = vi.fn();
    render(<Modal open={true} onClose={onClose} title="Test" />);
    const closeButton = screen.getByText(/test/i).closest("div.relative")?.querySelector("button");
    fireEvent.click(closeButton!);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("aplica clases correctas al modal", () => {
    render(<Modal open={true} onClose={vi.fn()} title="Test" />);
    const modalContent = screen.getByText(/test/i).closest("div.relative");
    expect(modalContent).toHaveClass("bg-white");
    expect(modalContent).toHaveClass("rounded-2xl");
    expect(modalContent).toHaveClass("shadow-xl");
    expect(modalContent).toHaveClass("border");
    expect(modalContent).toHaveClass("border-gray-100");
  });
});