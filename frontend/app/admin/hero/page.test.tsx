import { render, screen } from "@testing-library/react";
import AdminHeroRoute from "./page";

describe("AdminHeroRoute", () => {
	it("renders the hero section management page with media, crop, and seo fields", () => {
		render(<AdminHeroRoute />);
		expect(screen.getAllByText("Hero Section").length).toBeGreaterThan(0);
		expect(screen.getByText("Customize the storefront banner and promotional content")).toBeInTheDocument();
		expect(screen.getByText("Media upload")).toBeInTheDocument();
		expect(screen.getByText("Crop controls")).toBeInTheDocument();
		expect(screen.getByText("SEO details")).toBeInTheDocument();
	});
});
