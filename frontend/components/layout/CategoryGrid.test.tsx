import { render, screen } from "@testing-library/react";
import { CategoryGrid } from "./CategoryGrid";

describe("CategoryGrid", () => {
  it("renders category cards", () => {
    const categories = [["diya", "Diyas", "12 items"]] as const;
    render(<CategoryGrid categories={categories} />);
    expect(screen.getByText("Diyas")).toBeInTheDocument();
    expect(screen.getByText("12 items")).toBeInTheDocument();
  });
});