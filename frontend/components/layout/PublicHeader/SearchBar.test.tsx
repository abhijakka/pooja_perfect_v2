import { render, screen, fireEvent } from "@testing-library/react";
import { SearchBar } from "./SearchBar";
import type { StoreProduct } from "../../product/ProductCard/ProductGrid";

const product: StoreProduct = {
  id: "1",
  name: "Brass Diya",
  category: "pooja",
  categoryLabel: "Pooja",
  price: 499,
  oldPrice: 599,
  rating: "4.5",
  slug: "brass-diya",
  image: "/diya.jpg",
};

describe("SearchBar", () => {
  it("renders input and calls onQueryChange", () => {
    const onQueryChange = jest.fn();
    render(<SearchBar query="" suggestions={[]} onQueryChange={onQueryChange} onSearch={jest.fn()} />);
    const input = screen.getByLabelText("Search products");
    fireEvent.change(input, { target: { value: "diya" } });
    expect(onQueryChange).toHaveBeenCalledWith("diya");
  });

  it("shows suggestions when present", () => {
    render(<SearchBar query="diya" suggestions={[product]} onQueryChange={jest.fn()} onSearch={jest.fn()} />);
    expect(screen.getByText("Brass Diya")).toBeInTheDocument();
    expect(screen.getByText("₹499")).toBeInTheDocument();
  });

  it("submits the form", () => {
    const onSearch = jest.fn();
    render(<SearchBar query="diya" suggestions={[]} onQueryChange={jest.fn()} onSearch={onSearch} />);
    fireEvent.submit(screen.getByRole("searchbox"));
    expect(onSearch).toHaveBeenCalled();
  });
});