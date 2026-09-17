import { render, screen, act } from "@testing-library/react";
import { PoojaPointLoader } from "./PoojaPointLoader";

describe("PoojaPointLoader", () => {
  afterEach(() => jest.useRealTimers());

  it("shows the loader then hides after the delay", () => {
    jest.useFakeTimers();
    render(<PoojaPointLoader />);
    expect(screen.getByRole("status")).toBeInTheDocument();
    act(() => {
      jest.advanceTimersByTime(1200);
    });
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });
});