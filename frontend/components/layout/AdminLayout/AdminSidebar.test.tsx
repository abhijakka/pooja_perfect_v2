import { render, screen } from "@testing-library/react";
import { AdminSidebar } from "./AdminSidebar";

describe("AdminSidebar", () => {
  it("renders the admin navigation", () => {
    render(<AdminSidebar />);
    expect(screen.getByText("Admin navigation")).toBeInTheDocument();
  });
});