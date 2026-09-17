import { render, screen, fireEvent } from "@testing-library/react";
import { DatePicker } from "./DatePicker";

describe("DatePicker", () => {
  it("opens the calendar and reports a chosen date", () => {
    const onChange = jest.fn();
    render(<DatePicker value="" min="2026-09-01" onChange={onChange} />);
    fireEvent.click(screen.getByRole("button", { name: "Select date" }));
    expect(screen.getByRole("dialog", { name: "Choose delivery date" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Today" }));
    expect(onChange).toHaveBeenCalledWith("2026-09-01");
  });
});