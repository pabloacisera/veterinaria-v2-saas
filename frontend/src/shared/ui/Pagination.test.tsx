import { render, screen, fireEvent } from "@testing-library/react";
import { Pagination } from "./Pagination";

describe("Pagination", () => {
  it("no renderiza cuando totalPages <= 1", () => {
    const { container } = render(
      <Pagination page={1} totalPages={1} onPageChange={() => {}} />
    );
    expect(container.firstChild).toBeNull();
  });

  it("muestra página actual y total", () => {
    render(<Pagination page={2} totalPages={5} onPageChange={() => {}} />);
    expect(screen.getByText("Página 2 de 5")).toBeInTheDocument();
  });

  it("muestra botones Anterior y Siguiente", () => {
    render(<Pagination page={2} totalPages={5} onPageChange={() => {}} />);
    expect(screen.getByText("Anterior")).toBeInTheDocument();
    expect(screen.getByText("Siguiente")).toBeInTheDocument();
  });

  it("deshabilita Anterior en primera página", () => {
    render(<Pagination page={1} totalPages={5} onPageChange={() => {}} />);
    expect(screen.getByText("Anterior")).toBeDisabled();
  });

  it("deshabilita Siguiente en última página", () => {
    render(<Pagination page={5} totalPages={5} onPageChange={() => {}} />);
    expect(screen.getByText("Siguiente")).toBeDisabled();
  });

  it("llama a onPageChange con page - 1 al click Anterior", () => {
    const onPageChange = vi.fn();
    render(<Pagination page={3} totalPages={5} onPageChange={onPageChange} />);
    fireEvent.click(screen.getByText("Anterior"));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it("llama a onPageChange con page + 1 al click Siguiente", () => {
    const onPageChange = vi.fn();
    render(<Pagination page={3} totalPages={5} onPageChange={onPageChange} />);
    fireEvent.click(screen.getByText("Siguiente"));
    expect(onPageChange).toHaveBeenCalledWith(4);
  });
});
