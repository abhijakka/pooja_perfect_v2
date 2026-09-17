import { render, screen } from "@testing-library/react";
import { CartItem } from "./CartItem";

describe("CartItem", () => {
  it("renders the cart item placeholder", () => {
    render(<CartItem />);
    expect(screen.getByText("Cart item")).toBeInTheDocument();
  });
});