import { render, screen, fireEvent } from "@testing-library/react";
import { SubscriptionModal, type SubscriptionModalProps } from "./SubscriptionModal";

const plans: SubscriptionModalProps["plans"] = {
  "1_day": { name: "1 Day Pack", price: 49, kind: "date", count: 1 },
  "2_days": { name: "2 Days Pack", price: 98, kind: "date", count: 2 },
  monthly_1_day: { name: "1 Month - 1 Day", price: 49, kind: "weekday", count: 1 },
  monthly_2_days: { name: "1 Month - 2 Days", price: 98, kind: "weekday", count: 2 },
};

const baseProps: SubscriptionModalProps = {
  open: true,
  payGo: false,
  plan: "1_day",
  plans,
  products: [{ id: "diya", name: "Brass Diya", category: "Pooja", price: 349 }],
  selectedProducts: [],
  payGoQuery: "",
  dates: [],
  weekdays: [],
  deliveryTime: "",
  immediateAvailable: true,
  valid: false,
  onClose: jest.fn(),
  onProductSearch: jest.fn(),
  onAddProduct: jest.fn(),
  onDecreaseProduct: jest.fn(),
  onRemoveProduct: jest.fn(),
  onClearProducts: jest.fn(),
  onPlanSelect: jest.fn(),
  onDateChange: jest.fn(),
  onWeekdayChange: jest.fn(),
  onDeliveryTime: jest.fn(),
  onConfirm: jest.fn(),
};

describe("SubscriptionModal", () => {
  it("renders the plan modal and calls onClose", () => {
    const onClose = jest.fn();
    render(<SubscriptionModal {...baseProps} onClose={onClose} />);
    expect(screen.getByRole("heading", { name: "1 Day Pack" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(onClose).toHaveBeenCalled();
  });

  it("renders nothing when closed", () => {
    render(<SubscriptionModal {...baseProps} open={false} />);
    expect(screen.queryByRole("heading", { name: "1 Day Pack" })).not.toBeInTheDocument();
  });
});