import type { FormEvent } from "react";
import type { StoreProduct } from "../../product/ProductCard/ProductGrid";
import { SearchBar } from "./SearchBar";
import { Logo } from "./Logo";
import { HeaderActions } from "./HeaderActions";
import { CategoryNav } from "./CategoryNav";

type PublicHeaderProps = {
	query: string;
	suggestions: StoreProduct[];
	cartCount: number;
	wishlistCount: number;
	onQueryChange: (value: string) => void;
	onSearch: (event: FormEvent<HTMLFormElement>) => void;
	onProfile: () => void;
	onWishlist: () => void;
	onCart: () => void;
};

export function PublicHeader({ query, suggestions, cartCount, wishlistCount, onQueryChange, onSearch, onProfile, onWishlist, onCart }: PublicHeaderProps) {
	return (
		<>
			<div className="top-bar">Free delivery on orders above ₹999 · Handpicked essentials for every sacred ritual</div>
			<header className="navbar">
				<Logo />
				<SearchBar query={query} suggestions={suggestions} onQueryChange={onQueryChange} onSearch={onSearch} />
				<HeaderActions cartCount={cartCount} wishlistCount={wishlistCount} onProfile={onProfile} onWishlist={onWishlist} onCart={onCart} />
			</header>
			<CategoryNav />
		</>
	);
}
