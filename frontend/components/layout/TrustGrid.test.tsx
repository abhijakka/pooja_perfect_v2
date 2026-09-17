import { render, screen } from "@testing-library/react";
import { TrustGrid } from "./TrustGrid";

describe("TrustGrid", () => {
  it("renders trust cards", () => {
    const items = [["truck", "Fast delivery", "Delivered fast."]] as const;
    render(<TrustGrid items={items} />);
    expect(screen.getByText("Fast delivery")).toBeInTheDocument();
    expect(screen.getByText("Delivered fast.")).toBeInTheDocument();
  });
});