import { render, screen } from "@testing-library/react";
import { AdminHeader } from "./AdminHeader";

describe("AdminHeader", () => {
  it("renders the admin header", () => {
    render(<AdminHeader />);
    expect(screen.getByText("Admin header")).toBeInTheDocument();
  });
});