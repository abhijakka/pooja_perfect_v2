import { render, screen } from "@testing-library/react";
import ProductsPage from "./ProductsPage";

jest.mock("../../../services/api/products.api", () => ({
  productsApi: { list: jest.fn().mockRejectedValue(new Error("offline")) },
}));

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: jest.fn() }),
  useSearchParams: () => ({ get: () => null }),
}));
jest.mock("../../../hooks/useCart", () => ({
  useCart: () => ({ items: [], count: 0, total: 0, addItem: jest.fn(), removeItem: jest.fn() }),
}));
jest.mock("../../../hooks/useWishlist", () => ({
  useWishlist: () => ({ count: 0, contains: () => false, toggle: jest.fn() }),
}));
jest.mock("../../../components/layout/PublicHeader/PublicHeader", () => ({ PublicHeader: () => <header>Header</header> }));
jest.mock("../../../components/layout/PublicFooter/PublicFooter", () => ({ PublicFooter: () => <footer>Footer</footer> }));

describe("ProductsPage", () => {
  it("renders the fallback product listing when the backend is unavailable", async () => {
    render(<ProductsPage />);
    expect(screen.getByRole("heading", { name: "Shop all products" })).toBeInTheDocument();
    expect(await screen.findByText("Premium Brass Pooja Diya")).toBeInTheDocument();
    expect(screen.getByText("8 products")).toBeInTheDocument();
  });
});