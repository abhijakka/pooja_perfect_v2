"use client";

import { Icon } from "../../Icon";
import { useRouter } from "next/navigation";
import { useAuth } from "../../../hooks/useAuth";

type HeaderActionsProps = {
	cartCount: number;
	wishlistCount: number;
	onProfile: () => void;
	onWishlist: () => void;
	onCart: () => void;
};

export function HeaderActions(props: HeaderActionsProps) {
	const router = useRouter();
	const { user } = useAuth();
	const { cartCount, wishlistCount, onWishlist, onCart } = props;
	const openProfile = () => {
		if (user?.role_name === "admin") router.push("/admin");
		else if (user?.role_name === "customer") router.push("/my-account");
		else router.push("/login");
	};
	return (
		<div className="nav-actions">
			<button className="icon-button" onClick={openProfile} aria-label="Profile">
				<Icon name="user" />
			</button>
			<button className="icon-button" onClick={onWishlist} aria-label="Wishlist">
				<Icon name="heart" />
				<span className="badge">{wishlistCount}</span>
			</button>
			<button className="icon-button" onClick={onCart} aria-label="Cart">
				<Icon name="bag" />
				<span className="badge">{cartCount}</span>
			</button>
		</div>
	);
}
