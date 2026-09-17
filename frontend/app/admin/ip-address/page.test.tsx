import { render, screen } from "@testing-library/react";
import AdminIpRoute from "./page";

describe("AdminIpRoute", () => {
	it("renders the IP Addresses management page with its single IP policy table", () => {
		render(<AdminIpRoute />);
		expect(screen.getByText("IP Address Management")).toBeInTheDocument();
		expect(screen.getByPlaceholderText("Search IP address, location...")).toBeInTheDocument();
		expect(screen.getByText("IP Address")).toBeInTheDocument();
		expect(screen.getAllByText("Add IP").length).toBeGreaterThan(0);
		expect(screen.queryByPlaceholderText("Search IP, browser, device, OS...")).not.toBeInTheDocument();
	});
});