import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChatMessage } from "./ChatMessage";

function makeMsg(overrides = {}): import("@/entities/chat/types").ChatMessage {
  return {
    id: "1",
    role: "assistant",
    content: "Hola mundo",
    timestamp: new Date().toISOString(),
    ...overrides,
  };
}

describe("ChatMessage", () => {
  it("renderiza mensaje del usuario a la derecha", () => {
    const msg = makeMsg({ role: "user", content: "Hola" });
    const { container } = render(<ChatMessage message={msg} />);
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain("justify-end");
  });

  it("renderiza mensaje del asistente a la izquierda", () => {
    const msg = makeMsg({ role: "assistant", content: "Respuesta" });
    const { container } = render(<ChatMessage message={msg} />);
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain("justify-start");
  });

  it("renderiza contenido del mensaje", () => {
    const msg = makeMsg({ role: "user", content: "Contenido de prueba" });
    render(<ChatMessage message={msg} />);
    expect(screen.getByText("Contenido de prueba")).toBeInTheDocument();
  });

  it("renderiza markdown simple en mensajes del asistente", () => {
    const msg = makeMsg({ role: "assistant", content: "**negrita** y *cursiva*" });
    const { container } = render(<ChatMessage message={msg} />);
    expect(container.querySelector("strong")).toBeInTheDocument();
    expect(container.querySelector("em")).toBeInTheDocument();
  });

  it("muestra cursor de streaming cuando isStreaming es true", () => {
    const msg = makeMsg({ role: "assistant", content: "Parcial" });
    const { container } = render(<ChatMessage message={msg} isStreaming />);
    expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
  });
});
