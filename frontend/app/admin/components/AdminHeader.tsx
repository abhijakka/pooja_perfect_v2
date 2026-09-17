import { AdminIcon } from "./AdminIcon";

type AdminHeaderProps = {
	onMenu: () => void;
	query: string;
	onQuery: (value: string) => void;
	title?: string;
	subtitle?: string;
};

export function AdminHeader({
	onMenu,
	query,
	onQuery,
	title = "Dashboard",
	subtitle = "Store overview & performance",
}: AdminHeaderProps) {
	return <header className="admin-header"><div className="admin-header-left"><button className="admin-mobile-menu" type="button" onClick={onMenu} aria-label="Open menu"><AdminIcon name="menu" /></button><div><div className="admin-page-title">{title}</div><div className="admin-page-subtitle">{subtitle}</div></div></div><div className="admin-header-right"><label className="admin-search"><AdminIcon name="search" /><span className="sr-only">Search orders and products</span><input type="search" value={query} onChange={(event) => onQuery(event.target.value)} placeholder="Search orders, products..." /></label><button className="admin-header-icon" type="button" aria-label="Notifications" onClick={() => window.alert("12 new orders\n7 products low in stock\n3 orders awaiting processing")}><AdminIcon name="bell" /><span className="admin-notification-dot" /></button></div></header>;
}
