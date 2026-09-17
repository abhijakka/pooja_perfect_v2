import { render, screen } from "@testing-library/react";
import { PublicHeader } from "./PublicHeader";

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock("../../../hooks/useAuth", () => ({ useAuth: () => ({ user: null }) }));

describe("PublicHeader", () => {
  it("renders header with search and actions", () => {
    render(
      <PublicHeader
        query=""
        suggestions={[]}
        cartCount={1}
        wishlistCount={2}
        onQueryChange={jest.fn()}
        onSearch={jest.fn()}
        onProfile={jest.fn()}
        onWishlist={jest.fn()}
        onCart={jest.fn()}
      />
    );
    expect(
      screen.getByText("Free delivery on orders above ₹999 · Handpicked essentials for every sacred ritual")
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Search products")).toBeInTheDocument();
    expect(screen.getByLabelText("Cart")).toBeInTheDocument();
  });
});