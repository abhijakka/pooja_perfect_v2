import { render, screen } from "@testing-library/react";
import { CategoriesSection } from "./CategoriesSection";

describe("CategoriesSection", () => {
  it("renders the section with a view-all link", () => {
    const categories = [["diya", "Diyas", "12 items"]] as const;
    render(<CategoriesSection categories={categories} />);
    expect(screen.getByText("Shop by category")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "View all →" })).toHaveAttribute("href", "/products");
  });
});