import { render } from "@testing-library/react";
import { Icon } from "./Icon";

describe("Icon", () => {
  it("renders an svg for a known icon name", () => {
    const { container } = render(<Icon name="heart" />);
    expect(container.querySelector("svg")).toBeInTheDocument();
  });

  it("falls back to sparkle for unknown names", () => {
    const { container } = render(<Icon name="does-not-exist" />);
    expect(container.querySelector("svg")).toBeInTheDocument();
  });
});