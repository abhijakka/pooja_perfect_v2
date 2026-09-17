import { render, screen } from "@testing-library/react";
import { ProductCard } from "./ProductCard";

describe("ProductCard", () => {
  it("renders the product card", () => {
    render(<ProductCard />);
    expect(screen.getByText("Product")).toBeInTheDocument();
  });
});