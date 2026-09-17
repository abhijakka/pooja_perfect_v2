import { render, screen } from "@testing-library/react";
import { CartRemoveButton } from "./CartRemoveButton";

describe("CartRemoveButton", () => {
  it("renders a remove button", () => {
    render(<CartRemoveButton />);
    expect(screen.getByRole("button", { name: "Remove" })).toBeInTheDocument();
  });
});