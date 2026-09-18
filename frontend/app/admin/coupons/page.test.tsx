import { render, screen } from "@testing-library/react";
import AdminCouponsRoute from "./page";

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn(), replace: jest.fn() }) }));
jest.mock("react-redux", () => {
	const actual = jest.requireActual("react-redux");
	return { ...actual, useDispatch: Object.assign(() => jest.fn(), { withTypes: () => () => jest.fn() }) };
});

describe("AdminCouponsRoute", () => {
	it("renders the coupon management page with its coupon table", () => {
		render(<AdminCouponsRoute />);
		expect(screen.getByText("Coupon Management")).toBeInTheDocument();
		expect(screen.getByPlaceholderText("Search code or coupon name...")).toBeInTheDocument();
		expect(screen.getAllByText("Create Coupon").length).toBeGreaterThan(0);
		expect(screen.getByText("All Status")).toBeInTheDocument();
		expect(screen.getAllByText("All Discount Types").length).toBeGreaterThan(0);
	});
});