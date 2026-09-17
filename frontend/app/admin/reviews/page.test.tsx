import { render, screen } from "@testing-library/react";
import AdminReviewsRoute from "./page";

describe("AdminReviewsRoute", () => {
  it("renders the product reviews dashboard", () => {
    render(<AdminReviewsRoute />);
    expect(screen.getAllByText("Product Reviews").length).toBeGreaterThan(0);
    expect(screen.getByText("Customer feedback and product ratings")).toBeInTheDocument();
  });
});
