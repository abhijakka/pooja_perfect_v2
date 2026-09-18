import { render, screen } from "@testing-library/react";
import AdminPage from "./page";

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn(), replace: jest.fn() }) }));
jest.mock("react-redux", () => {
	const actual = jest.requireActual("react-redux");
	return { ...actual, useDispatch: Object.assign(() => jest.fn(), { withTypes: () => () => jest.fn() }) };
});

describe("AdminPage", () => {
  it("renders the admin dashboard", () => {
    render(<AdminPage />);
    expect(screen.getByRole("heading", { name: /Good afternoon/ })).toBeInTheDocument();
    expect(screen.getByText("Sales Overview")).toBeInTheDocument();
  });
});