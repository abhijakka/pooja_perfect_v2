import { render, screen } from "@testing-library/react";
import { AdminBreadcrumb } from "./AdminBreadcrumb";

describe("AdminBreadcrumb", () => {
  it("renders a breadcrumb nav", () => {
    render(<AdminBreadcrumb />);
    expect(screen.getByRole("navigation", { name: "Breadcrumb" })).toBeInTheDocument();
  });
});