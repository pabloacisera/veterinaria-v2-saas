import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChatInput } from "./ChatInput";

describe("ChatInput", () => {
  it("renderiza el textarea y boton", () => {
    render(<ChatInput onSend={() => {}} />);
    expect(screen.getByPlaceholderText("Escribí tu mensaje...")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Enviar" })).toBeInTheDocument();
  });

  it("deshabilita boton si el input esta vacio", () => {
    render(<ChatInput onSend={() => {}} />);
    expect(screen.getByRole("button", { name: "Enviar" })).toBeDisabled();
  });

  it("habilita boton cuando hay texto", async () => {
    const user = userEvent.setup();
    render(<ChatInput onSend={() => {}} />);
    const input = screen.getByPlaceholderText("Escribí tu mensaje...");
    await user.type(input, "Hola");
    expect(screen.getByRole("button", { name: "Enviar" })).not.toBeDisabled();
  });

  it("llama a onSend y limpia el input al enviar", async () => {
    const onSend = vi.fn();
    const user = userEvent.setup();
    render(<ChatInput onSend={onSend} />);
    const input = screen.getByPlaceholderText("Escribí tu mensaje...");
    await user.type(input, "Hola mundo");
    await user.click(screen.getByRole("button", { name: "Enviar" }));
    expect(onSend).toHaveBeenCalledWith("Hola mundo");
    expect(input).toHaveValue("");
  });

  it("deshabilita cuando disabled es true", () => {
    render(<ChatInput onSend={() => {}} disabled />);
    expect(screen.getByPlaceholderText("Escribí tu mensaje...")).toBeDisabled();
    expect(screen.getByRole("button", { name: "Enviar" })).toBeDisabled();
  });

  it("muestra placeholder personalizado", () => {
    render(<ChatInput onSend={() => {}} placeholder="Test placeholder" />);
    expect(screen.getByPlaceholderText("Test placeholder")).toBeInTheDocument();
  });
});
