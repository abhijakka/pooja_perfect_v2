import { render, screen } from "@testing-library/react";
import AdminIpRoute from "./page";

describe("AdminIpRoute", () => {
	it("renders the IP Addresses management page with its single visitor tracking table", () => {
		render(<AdminIpRoute />);
		expect(screen.getByText("IP Address Management")).toBeInTheDocument();
		expect(screen.getByPlaceholderText("Search IP, device, browser, OS...")).toBeInTheDocument();
		expect(screen.getAllByText("IP Address").length).toBeGreaterThan(0);
		expect(screen.getAllByText("Add IP").length).toBeGreaterThan(0);
		expect(screen.getByText("All Status")).toBeInTheDocument();
		expect(screen.getAllByText("Blocked").length).toBeGreaterThan(0);
		expect(screen.queryByPlaceholderText("Search IP address, location...")).not.toBeInTheDocument();
	});
});