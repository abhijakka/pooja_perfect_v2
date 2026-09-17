import { render, screen } from "@testing-library/react";
import { OfferBanner } from "./OfferBanner";

describe("OfferBanner", () => {
  it("renders the offer banner with the promo code", () => {
    render(<OfferBanner />);
    expect(screen.getByText("Make every ritual feel special.")).toBeInTheDocument();
    expect(screen.getByText("POOJA10")).toBeInTheDocument();
  });
});