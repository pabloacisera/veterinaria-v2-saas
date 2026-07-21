import { vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Pagination } from "./Pagination";

describe("Pagination", () => {
  it("renders page info", () => {
    render(<Pagination page={2} totalPages={5} totalItems={100} onPageChange={vi.fn()} />);
    expect(screen.getByText("Página 2 de 5 (100 registros)")).toBeInTheDocument();
  });

  it("hides when totalPages is 1", () => {
    const { container } = render(
      <Pagination page={1} totalPages={1} totalItems={5} onPageChange={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it("calls onPageChange with previous page", async () => {
    const onChange = vi.fn();
    render(<Pagination page={3} totalPages={5} totalItems={100} onPageChange={onChange} />);
    await userEvent.click(screen.getByText("Anterior"));
    expect(onChange).toHaveBeenCalledWith(2);
  });

  it("calls onPageChange with next page", async () => {
    const onChange = vi.fn();
    render(<Pagination page={2} totalPages={5} totalItems={100} onPageChange={onChange} />);
    await userEvent.click(screen.getByText("Siguiente"));
    expect(onChange).toHaveBeenCalledWith(3);
  });

  it("disables Previous on first page", () => {
    render(<Pagination page={1} totalPages={5} totalItems={100} onPageChange={vi.fn()} />);
    expect(screen.getByText("Anterior")).toBeDisabled();
  });

  it("disables Next on last page", () => {
    render(<Pagination page={5} totalPages={5} totalItems={100} onPageChange={vi.fn()} />);
    expect(screen.getByText("Siguiente")).toBeDisabled();
  });
});
