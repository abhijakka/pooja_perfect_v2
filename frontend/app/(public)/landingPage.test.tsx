import { screen } from "@testing-library/react";
import Storefront from "./landingPage";
import { renderWithProviders } from "../../store/test-utils";

jest.mock("../../services/api/categories.api", () => ({
  categoriesApi: { list: jest.fn().mockResolvedValue({ categories: [] }) },
}));
jest.mock("../../services/api/products.api", () => ({
  productsApi: { featured: jest.fn().mockResolvedValue({ products: { items: [] } }) },
}));
jest.mock("../../services/api/hero.api", () => ({
  heroesApi: { list: jest.fn().mockResolvedValue({ heroes: [] }) },
}));

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock("../../hooks/useCart", () => ({
  useCart: () => ({ items: [], count: 0, total: 0, addItem: jest.fn(), removeItem: jest.fn() }),
}));
jest.mock("../../hooks/useWishlist", () => ({
  useWishlist: () => ({ items: [], count: 0, toggle: jest.fn() }),
}));
jest.mock("../../components/layout/PublicHeader/PublicHeader", () => ({ PublicHeader: () => <header>Header</header> }));
jest.mock("../../components/layout/PublicFooter/PublicFooter", () => ({ PublicFooter: () => <footer>Footer</footer> }));
jest.mock("../../components/subscription/SubscriptionSection", () => ({ SubscriptionSection: () => <section>Subscriptions</section> }));
jest.mock("../../components/layout/OfferBanner", () => ({ OfferBanner: () => <div>Offer</div> }));
jest.mock("../../components/layout/TrustSection", () => ({ TrustSection: () => <div>Trust</div> }));
jest.mock("../../components/layout/HeroSection", () => ({ HeroSection: () => <section>Hero</section> }));
jest.mock("../../components/layout/CategoriesSection", () => ({ CategoriesSection: () => <section>Categories</section> }));
jest.mock("../../components/product/ProductCard/ProductsSection", () => ({ ProductsSection: () => <section>Products</section> }));

describe("Storefront", () => {
  it("renders the storefront sections", () => {
    renderWithProviders(<Storefront />);
    expect(screen.getByText("Hero")).toBeInTheDocument();
    expect(screen.getByText("Products")).toBeInTheDocument();
    expect(screen.getByText("Subscriptions")).toBeInTheDocument();
    expect(screen.getByText("Footer")).toBeInTheDocument();
  });
});