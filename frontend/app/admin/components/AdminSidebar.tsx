"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { authApi } from "../../../services/api/auth.api";
import { useAppDispatch } from "../../../store/hooks";
import { logout } from "../../../store/slices/authSlice";
import { AdminIcon } from "./AdminIcon";

type AdminSidebarProps = { open: boolean; onClose: () => void; activeHref?: string };

const sections = [
	{ label: "Overview", items: [{ label: "Dashboard", href: "/admin", icon: "grid" as const }, { label: "Hero Section", href: "/admin/hero", icon: "image" as const }] },
	{ label: "Catalog", items: [{ label: "Products", href: "/admin/products", icon: "products" as const }, { label: "Product Reviews", href: "/admin/reviews", icon: "review" as const }, { label: "Categories", href: "/admin/categories", icon: "category" as const }, { label: "Coupons", href: "/admin/coupons", icon: "discount" as const }] },
	{ label: "Customers", items: [{ label: "Customers", href: "/admin/customers", icon: "customers" as const }, { label: "Wishlist", href: "/admin/wishlist", icon: "wishlist" as const }, { label: "Customer Chat", href: "/admin/chat", icon: "chat" as const }] },
	{ label: "Analytics", items: [{ label: "Sales Analytics", href: "/admin/analytics", icon: "analytics" as const }, { label: "Reports", href: "/admin/reports", icon: "money" as const }] },
	{ label: "Security", items: [{ label: "IP Addresses", href: "/admin/ip-address", icon: "ip" as const }, { label: "Activity Logs", href: "/admin/logs", icon: "note" as const }] },
	{ label: "System", items: [{ label: "Settings", href: "/admin/settings", icon: "settings" as const }] },
];

export function AdminSidebar({ open, onClose, activeHref }: AdminSidebarProps) {
	const router = useRouter();
	const dispatch = useAppDispatch();
	const signOut = async () => {
		if (!window.confirm("Are you sure you want to sign out?")) return;
		try { await authApi.logout(); } finally { dispatch(logout()); router.replace("/"); }
	};
	return <><aside className={`admin-sidebar ${open ? "is-open" : ""}`}>
		<div className="admin-sidebar-brand"><div className="admin-brand-icon"><AdminIcon name="logo" /></div><div><div className="admin-brand-name">Pooja<span>Point</span></div><div className="admin-label">Administration</div></div></div>
		<nav className="admin-sidebar-nav">{sections.map((section) => <div key={section.label}><div className="admin-nav-section">{section.label}</div>{section.items.map((item) => <Link key={item.href} href={item.href} className={`admin-nav-item ${activeHref === item.href || (activeHref === undefined && item.label === "Dashboard") ? "active" : ""}`} onClick={onClose}><AdminIcon name={item.icon} />{item.label}{item.label === "Orders" && <span className="admin-nav-badge">12</span>}</Link>)}</div>)}
			<div className="admin-nav-section">Operations</div><Link href="/admin/orders" className={`admin-nav-item ${activeHref === "/admin/orders" ? "active" : ""}`} onClick={onClose}><AdminIcon name="orders" />Orders<span className="admin-nav-badge">12</span></Link><Link href="/" className="admin-nav-item" onClick={onClose}><AdminIcon name="eye" />Storefront</Link>
			<button className="admin-nav-item admin-signout" type="button" onClick={() => void signOut()}><AdminIcon name="logout" />Sign Out</button>
		</nav>
		<div className="admin-sidebar-bottom"><div className="admin-profile"><div className="admin-avatar">AD</div><div><div className="admin-name">Admin</div><div className="admin-role">Store Administrator</div></div></div></div>
	</aside><button className={`admin-overlay ${open ? "show" : ""}`} type="button" aria-label="Close menu" onClick={onClose} /></>;
}
