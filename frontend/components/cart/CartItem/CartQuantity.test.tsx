import { render, screen } from "@testing-library/react";
import { CartQuantity } from "./CartQuantity";

describe("CartQuantity", () => {
  it("renders a quantity input defaulting to 1", () => {
    render(<CartQuantity />);
    const input = screen.getByLabelText("Quantity");
    expect(input).toHaveValue(1);
    expect(input).toHaveAttribute("min", "1");
  });
});