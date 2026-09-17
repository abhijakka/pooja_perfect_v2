import { Icon } from "../../Icon";
import Link from "next/link";
import { useChat } from "../../../hooks/useChat";

type MobileBottomNavProps = {
  activeNav: string;
  wishlistCount: number;
  cartCount: number;
  onNavChange: (key: string) => void;
  onWishlist: () => void;
  onProfile: () => void;
};

const navigationItems = [
  ["home", "Home", "#top", "home"],
  ["wishlist", "Wishlist", "/wishlist", "heart"],
  ["shop", "Shop", "#products", "bag"],
  ["profile", "Profile", "#top", "user"],
  ["support", "Support", "#support", "chat"],
] as const;

export function MobileBottomNav({ activeNav, wishlistCount, cartCount, onNavChange, onWishlist, onProfile }: MobileBottomNavProps) {
  const { openChat } = useChat();

  return (
    <nav className="mobile-bottom-nav" aria-label="Mobile navigation">
      {navigationItems.map(([key, label, href, icon]) => (
        <Link
          className={`mobile-bottom-nav-item ${activeNav === key ? "active" : ""}`}
          href={key === "shop" ? "/cart" : key === "support" ? "#support" : href}
          onClick={() => {
            onNavChange(key);
            if (key === "wishlist") onWishlist();
            if (key === "profile") onProfile();
            if (key === "support") openChat();
          }}
          key={key}
        >
          <span className="mobile-bottom-nav-icon-wrap">
            <Icon name={icon} />
            {key === "wishlist" && wishlistCount > 0 && <span className="mobile-bottom-nav-badge">{wishlistCount}</span>}
            {key === "shop" && cartCount > 0 && <span className="mobile-bottom-nav-badge">{cartCount}</span>}
          </span>
          <span className="mobile-bottom-nav-label">{label}</span>
        </Link>
      ))}
    </nav>
  );
}
