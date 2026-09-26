import { screen } from "@testing-library/react";
import { CategoryNav } from "./CategoryNav";
import { renderWithProviders } from "../../../store/test-utils";
import { makeStore } from "../../../store";
import { setUser } from "../../../store/slices/authSlice";

jest.mock("../../../services/api/categories.api", () => ({
	categoriesApi: { list: () => Promise.reject(new Error("offline")) },
}));

function renderAs(role?: "customer" | "admin") {
	const store = makeStore();
	if (role) store.dispatch(setUser({ id: "u1", name: "Test", email: "t@example.com", role_name: role }));
	return renderWithProviders(<CategoryNav />, { store });
}

describe("CategoryNav authorization", () => {
	it("hides My Account and My Orders from unauthorized visitors", () => {
		renderAs();
		expect(screen.queryByText("My Account")).not.toBeInTheDocument();
		expect(screen.queryByText("My Orders")).not.toBeInTheDocument();
		expect(screen.getByText("Shop All")).toBeInTheDocument();
	});

	it("shows My Account and My Orders for an authenticated customer", () => {
		renderAs("customer");
		expect(screen.getByText("My Account")).toHaveAttribute("href", "/my-account");
		expect(screen.getByText("My Orders")).toHaveAttribute("href", "/my-orders");
	});

	it("never treats an admin as a customer", () => {
		renderAs("admin");
		expect(screen.queryByText("My Account")).not.toBeInTheDocument();
		expect(screen.queryByText("My Orders")).not.toBeInTheDocument();
	});

	it("uses next/link so navigating does not tear down the app store", () => {
		renderAs("customer");
		expect(screen.getByText("Shop All").closest("a")).not.toBeNull();
	});
});
