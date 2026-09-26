import { MobileBottomNav } from "./MobileBottomNav";
import Link from "next/link";

type PublicFooterProps = {
	activeNav: string;
	wishlistCount: number;
	cartCount: number;
	onNavChange: (key: string) => void;
	onWishlist: () => void;
	onProfile: () => void;
};

export function PublicFooter({ activeNav, wishlistCount, cartCount, onNavChange, onWishlist, onProfile }: PublicFooterProps) {
	return (
		<footer className="footer" id="support">
			<div className="footer-grid">
				<div className="footer-brand">
					<h3>PoojaPoint</h3>
					<p>A calm, modern destination for pooja essentials, sacred décor, gifting and everyday rituals.</p>
					<p>Inspired by the best parts of modern Indian devotional shopping.</p>
				</div>
					<div>
						<h3>Shop</h3>
						<Link href="/products">Pooja Products</Link><Link href="/products?category=idols">Idols</Link><Link href="/products?category=decor">Decor</Link><Link href="/products?category=gifting">Gifting</Link>
					</div>
				<div>
					<h3>Help</h3>
					<a href="#support">Contact us</a><a href="#support">Shipping</a><a href="#support">Returns</a><a href="#support">FAQ</a>
				</div>
				<div>
					<h3>Connect</h3>
					<p>Instagram · Facebook</p><p>support@poojapoint.com</p><p>mypoojabox.in</p>
				</div>
			</div>
			<div className="copyright">© {new Date().getFullYear()} PoojaPoint. All rights reserved.</div>
			<MobileBottomNav
				activeNav={activeNav}
				wishlistCount={wishlistCount}
				cartCount={cartCount}
				onNavChange={onNavChange}
				onWishlist={onWishlist}
				onProfile={onProfile}
			/>
		</footer>
	);
}
