import { render, screen, fireEvent } from "@testing-library/react";
import { HeaderActions } from "./HeaderActions";

const push = jest.fn();

jest.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
jest.mock("../../../hooks/useAuth", () => ({ useAuth: () => ({ user: null }) }));

describe("HeaderActions", () => {
  it("renders action buttons with counts", () => {
    render(
      <HeaderActions
        cartCount={2}
        wishlistCount={3}
        onProfile={jest.fn()}
        onWishlist={jest.fn()}
        onCart={jest.fn()}
      />
    );
    expect(screen.getByLabelText("Cart")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("calls handlers on click", () => {
    const onCart = jest.fn();
    render(
      <HeaderActions
        cartCount={0}
        wishlistCount={0}
        onProfile={jest.fn()}
        onWishlist={jest.fn()}
        onCart={onCart}
      />
    );
    fireEvent.click(screen.getByLabelText("Cart"));
    expect(onCart).toHaveBeenCalled();
  });

  it("opens the login page for guests", () => {
    render(
      <HeaderActions
        cartCount={0}
        wishlistCount={0}
        onProfile={jest.fn()}
        onWishlist={jest.fn()}
        onCart={jest.fn()}
      />
    );

    fireEvent.click(screen.getByLabelText("Profile"));
    expect(push).toHaveBeenCalledWith("/login");
  });
});