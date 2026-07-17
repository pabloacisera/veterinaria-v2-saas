import { render, screen, fireEvent } from "@testing-library/react";
import { Table } from "./Table";

interface TestRow {
  id: string;
  name: string;
  value: number;
}

describe("Table", () => {
  const columns = [
    { header: "Nombre", accessor: "name" as keyof TestRow },
    { header: "Valor", accessor: "value" as keyof TestRow },
    {
      header: "Acciones",
      render: (row: TestRow) => <button data-testid={`action-${row.id}`}>Acción</button>,
    },
  ];

  const data: TestRow[] = [
    { id: "1", name: "Item 1", value: 10 },
    { id: "2", name: "Item 2", value: 20 },
    { id: "3", name: "Item 3", value: 30 },
  ];

  it("renderiza la tabla con headers", () => {
    render(<Table columns={columns} data={data} keyExtractor={(row) => row.id} />);
    expect(screen.getByText(/nombre/i)).toBeInTheDocument();
    expect(screen.getByText(/valor/i)).toBeInTheDocument();
    expect(screen.getByText(/acciones/i)).toBeInTheDocument();
  });

  it("renderiza todas las filas de datos", () => {
    render(<Table columns={columns} data={data} keyExtractor={(row) => row.id} />);
    expect(screen.getByText(/item 1/i)).toBeInTheDocument();
    expect(screen.getByText(/item 2/i)).toBeInTheDocument();
    expect(screen.getByText(/item 3/i)).toBeInTheDocument();
  });

  it("muestra mensaje vacío cuando no hay datos", () => {
    render(<Table columns={columns} data={[]} keyExtractor={(row) => row.id} />);
    expect(screen.getByText(/no hay datos/i)).toBeInTheDocument();
  });

  it("muestra mensaje vacío personalizado", () => {
    render(
      <Table columns={columns} data={[]} keyExtractor={(row) => row.id} emptyMessage="Sin resultados" />
    );
    expect(screen.getByText(/sin resultados/i)).toBeInTheDocument();
  });

  it("muestra loading cuando loading=true", () => {
    render(<Table columns={columns} data={data} keyExtractor={(row) => row.id} loading />);
    expect(screen.getByText(/cargando/i)).toBeInTheDocument();
  });

  it("llama a onRowClick al hacer click en una fila", () => {
    const onRowClick = vi.fn();
    render(
      <Table columns={columns} data={data} keyExtractor={(row) => row.id} onRowClick={onRowClick} />
    );
    fireEvent.click(screen.getByText(/item 1/i).closest("tr")!);
    expect(onRowClick).toHaveBeenCalledWith(data[0]);
  });

  it("no tiene cursor pointer cuando no hay onRowClick", () => {
    render(<Table columns={columns} data={data} keyExtractor={(row) => row.id} />);
    const row = screen.getByText(/item 1/i).closest("tr");
    expect(row).not.toHaveClass("cursor-pointer");
  });

  it("usa render function personalizada", () => {
    render(<Table columns={columns} data={data} keyExtractor={(row) => row.id} />);
    expect(screen.getByTestId("action-1")).toBeInTheDocument();
    expect(screen.getByTestId("action-2")).toBeInTheDocument();
    expect(screen.getByTestId("action-3")).toBeInTheDocument();
  });

  it("aplica className a columnas", () => {
    const columnsWithClass = [
      { header: "Test", accessor: "name" as keyof TestRow, className: "text-right" },
    ];
    render(<Table columns={columnsWithClass} data={data} keyExtractor={(row) => row.id} />);
    const header = screen.getByText(/test/i);
    expect(header).toHaveClass("text-right");
  });
});
