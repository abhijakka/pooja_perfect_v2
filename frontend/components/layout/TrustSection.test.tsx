import { render, screen } from "@testing-library/react";
import { TrustSection } from "./TrustSection";

describe("TrustSection", () => {
  it("renders the trust section", () => {
    render(<TrustSection />);
    expect(screen.getByText("Fast delivery")).toBeInTheDocument();
    expect(screen.getByText("Secure payments")).toBeInTheDocument();
  });
});