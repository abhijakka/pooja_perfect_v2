import { render, screen } from "@testing-library/react";
import { MobileHeader } from "./MobileHeader";

describe("MobileHeader", () => {
  it("renders the mobile header", () => {
    render(<MobileHeader />);
    expect(screen.getByText("Mobile header")).toBeInTheDocument();
  });
});