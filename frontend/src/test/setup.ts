import "@testing-library/jest-dom";
import { cleanup } from "@testing-library/react";
import { afterEach, vi, expect } from "vitest";

global.expect = expect;

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  localStorage.clear();
  sessionStorage.clear();
});

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

Object.defineProperty(window, "scrollTo", {
  writable: true,
  value: vi.fn(),
});

vi.stubGlobal("location", {
  ...window.location,
  href: "",
  assign: vi.fn(),
  replace: vi.fn(),
  reload: vi.fn(),
});
