import { screen } from "@testing-library/react";
import { CategoryNav } from "./CategoryNav";
import { renderWithProviders } from "../../../store/test-utils";

describe("CategoryNav", () => {
  it("renders all category links", () => {
    renderWithProviders(<CategoryNav />);
    expect(screen.getByRole("navigation", { name: "Categories" })).toBeInTheDocument();
    expect(screen.getByText("Shop All")).toBeInTheDocument();
    expect(screen.getByText("Track Order")).toBeInTheDocument();
    expect(screen.getByText("Gifting")).toHaveAttribute("href", "/products?category=gifting");
  });
});