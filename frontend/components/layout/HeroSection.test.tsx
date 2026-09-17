import { render, screen, fireEvent } from "@testing-library/react";
import { HeroSection } from "./HeroSection";

describe("HeroSection", () => {
  it("renders hero with shop now button", () => {
    const onExplore = jest.fn();
    render(<HeroSection onExplore={onExplore} />);
    expect(screen.getByText("SIGNATURE EDIT")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Shop now" }));
    expect(onExplore).toHaveBeenCalled();
  });
});