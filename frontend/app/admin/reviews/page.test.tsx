import { render, screen } from "@testing-library/react";
import AdminReviewsRoute from "./page";

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn(), replace: jest.fn() }) }));
jest.mock("react-redux", () => {
	const actual = jest.requireActual("react-redux");
	return { ...actual, useDispatch: Object.assign(() => jest.fn(), { withTypes: () => () => jest.fn() }) };
});

describe("AdminReviewsRoute", () => {
  it("renders the product reviews dashboard", () => {
    render(<AdminReviewsRoute />);
    expect(screen.getAllByText("Product Reviews").length).toBeGreaterThan(0);
    expect(screen.getByText("Customer feedback and product ratings")).toBeInTheDocument();
  });
});
