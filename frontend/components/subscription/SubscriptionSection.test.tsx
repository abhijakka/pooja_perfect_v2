import { render, screen, fireEvent } from "@testing-library/react";
import { SubscriptionSection } from "./SubscriptionSection";

describe("SubscriptionSection", () => {
  it("renders the plans and calls onPlanSelect", () => {
    const onPlanSelect = jest.fn();
    render(<SubscriptionSection onPlanSelect={onPlanSelect} onPayGoSelect={jest.fn()} />);
    expect(screen.getByText("Pay As You Go")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Choose 1 Day" }));
    expect(onPlanSelect).toHaveBeenCalledWith("1_day");
  });

  it("calls onPayGoSelect for the flexible plan", () => {
    const onPayGoSelect = jest.fn();
    render(<SubscriptionSection onPlanSelect={jest.fn()} onPayGoSelect={onPayGoSelect} />);
    fireEvent.click(screen.getByRole("button", { name: "Customize Pack" }));
    expect(onPayGoSelect).toHaveBeenCalled();
  });
});