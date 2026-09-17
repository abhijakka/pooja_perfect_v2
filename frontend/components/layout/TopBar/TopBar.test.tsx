import { render, screen } from "@testing-library/react";
import { TopBar } from "./TopBar";

describe("TopBar", () => {
  it("renders the top bar", () => {
    render(<TopBar />);
    expect(screen.getByRole("banner")).toHaveTextContent("PoojaPoint");
  });
});