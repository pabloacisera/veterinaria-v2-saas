import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Landing } from "../Landing";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

function renderLanding() {
  return render(
    <MemoryRouter>
      <Landing />
    </MemoryRouter>
  );
}

describe("Landing - Islas de acceso", () => {
  beforeEach(() => {
    mockNavigate.mockReset();
  });

  it("muestra la isla de acceso al portal de clientes", () => {
    renderLanding();
    expect(
      screen.getByText("¿Sos dueño de una mascota?")
    ).toBeInTheDocument();
    expect(
      screen.getByText("Ingresar al portal de mi mascota")
    ).toBeInTheDocument();
  });

  it("navega a /cliente/acceso al hacer click en el botón del portal", () => {
    renderLanding();
    const btn = screen.getByText("Ingresar al portal de mi mascota");
    fireEvent.click(btn);
    expect(mockNavigate).toHaveBeenCalledWith("/cliente/acceso");
  });

  it("muestra link discreto de admin en el footer", () => {
    renderLanding();
    const adminLink = screen.getByLabelText("Acceso administrador");
    expect(adminLink).toBeInTheDocument();
    expect(adminLink).toHaveAttribute("href", "/access_role/admin/developer");
  });

  it("el link de admin tiene estilos discretos (text-xs text-gray-300)", () => {
    renderLanding();
    const adminLink = screen.getByLabelText("Acceso administrador");
    expect(adminLink.className).toContain("text-xs");
    expect(adminLink.className).toContain("text-gray-300");
  });

  it("la isla de clientes tiene el emoji de mascota con rol img", () => {
    renderLanding();
    const emoji = screen.getByRole("img", { name: "Mascota" });
    expect(emoji).toBeInTheDocument();
  });
});
