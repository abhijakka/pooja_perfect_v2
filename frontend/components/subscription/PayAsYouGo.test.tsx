import { render, screen } from "@testing-library/react";
import { ProductSearch } from "./PayAsYouGo/ProductSearch";
import { QuantityControl } from "./PayAsYouGo/QuantityControl";
import { SelectedProducts } from "./PayAsYouGo/SelectedProducts";
import { ProductResult } from "./PayAsYouGo/ProductResult";

describe("PayAsYouGo components", () => {
  it("renders the product search input", () => {
    render(<ProductSearch />);
    expect(screen.getByLabelText("Search products")).toBeInTheDocument();
  });

  it("renders the quantity control", () => {
    render(<QuantityControl />);
    expect(screen.getByLabelText("Quantity")).toBeInTheDocument();
  });

  it("renders selected products", () => {
    render(<SelectedProducts />);
    expect(screen.getByText("Selected products")).toBeInTheDocument();
  });

  it("renders a product result", () => {
    render(<ProductResult />);
    expect(screen.getByText("Product result")).toBeInTheDocument();
  });
});