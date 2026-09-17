import { render, screen } from "@testing-library/react";
import { Logo } from "./Logo";

describe("Logo", () => {
  it("renders a link to home", () => {
    render(<Logo />);
    const link = screen.getByRole("link", { name: "PoojaPoint home" });
    expect(link).toHaveAttribute("href", "/");
  });
});