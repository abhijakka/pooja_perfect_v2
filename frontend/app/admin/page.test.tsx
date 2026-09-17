import { render, screen } from "@testing-library/react";
import AdminPage from "./page";

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn() }) }));

describe("AdminPage", () => {
  it("renders the admin dashboard", () => {
    render(<AdminPage />);
    expect(screen.getByRole("heading", { name: /Good afternoon/ })).toBeInTheDocument();
    expect(screen.getByText("Sales Overview")).toBeInTheDocument();
  });
});