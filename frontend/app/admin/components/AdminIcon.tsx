import type { IconName } from "./dashboard-data";

type AdminIconProps = { name: IconName; className?: string };

export function AdminIcon({ name, className = "" }: AdminIconProps) {
	return <svg className={`admin-icon ${className}`} aria-hidden="true"><use href={`#admin-${name}`} /></svg>;
}

export function AdminIconSprite() {
	return <svg className="admin-icon-library" aria-hidden="true">
		<symbol id="admin-ai" viewBox="0 0 24 24"><path d="m12 3 1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5L12 3Z"/><path d="m19 16 .7 2.3L22 19l-2.3.7L19 22l-.7-2.3L16 19l2.3-.7L19 16Z"/></symbol>
		<symbol id="admin-logo" viewBox="0 0 24 24"><path d="M12 3C8 3 5 6 5 10c0 5 4 8 7 11 3-3 7-6 7-11 0-4-3-7-7-7Z"/><path d="M8 10c1.5-2 3-2 4 0 1-2 2.5-2 4 0"/></symbol>
		<symbol id="admin-grid" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></symbol>
		<symbol id="admin-orders" viewBox="0 0 24 24"><path d="m12 2 9 5v10l-9 5-9-5V7l9-5Z"/><path d="m3 7 9 5 9-5M12 12v10"/></symbol>
		<symbol id="admin-products" viewBox="0 0 24 24"><path d="m4 7 8-4 8 4-8 4-8-4ZM4 7v10l8 4 8-4V7M12 11v10"/></symbol>
		<symbol id="admin-review" viewBox="0 0 24 24"><path d="m12 2 2.7 5.3L20 10l-5.3 2.7L12 18l-2.7-5.3L4 10l5.3-2.7L12 2Z"/><path d="M18 15.5 19.5 18l2.5.5-2.5.5L18 21l-.5-2.5-2.5-.5 2.5-.5L18 15.5Z"/></symbol>
		<symbol id="admin-customers" viewBox="0 0 24 24"><circle cx="9" cy="8" r="4"/><path d="M2 21c0-4 3-7 7-7s7 3 7 7M17 4c2 .5 3.5 2 3.5 4s-1.5 3.5-3.5 4M18 15c2 .8 3.5 2.5 4 5"/></symbol>
		<symbol id="admin-category" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></symbol>
		<symbol id="admin-wishlist" viewBox="0 0 24 24"><path d="M20.8 8.5C20.8 13.5 12 20 12 20S3.2 13.5 3.2 8.5A5 5 0 0 1 12 6a5 5 0 0 1 8.8 2.5Z"/></symbol>
		<symbol id="admin-analytics" viewBox="0 0 24 24"><path d="M4 19V5M4 19h17m-14-4 3-4 3 2 5-7"/></symbol>
		<symbol id="admin-discount" viewBox="0 0 24 24"><path d="m20 13-7 7-9-9V4h7l9 9Z"/><circle cx="7.5" cy="7.5" r="1"/></symbol>
		<symbol id="admin-settings" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="m19.4 15 .1-6 2-1.5-2-3.4-2.4 1a8 8 0 0 0-5.2-3L11.5 2h-3L8 4.1a8 8 0 0 0-4.3 3l-2-.9-2 3.4L2 11a8 8 0 0 0 0 2l-2 1.4 2 3.4 2-.9a8 8 0 0 0 4.3 3l.5 2.1h3l.5-2.1a8 8 0 0 0 4.3-3l2 .9 2-3.4-2-1.4Z"/></symbol>
		<symbol id="admin-search" viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></symbol>
		<symbol id="admin-eye" viewBox="0 0 24 24"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></symbol>
		<symbol id="admin-bell" viewBox="0 0 24 24"><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/></symbol>
		<symbol id="admin-chat" viewBox="0 0 24 24"><path d="M20 11.5a7.5 7.5 0 0 1-8 7.5 9 9 0 0 1-4-.9L3 20l1.8-4.2A7.2 7.2 0 0 1 4 11.5 7.5 7.5 0 0 1 12 4a7.5 7.5 0 0 1 8 7.5Z"/></symbol>
		<symbol id="admin-menu" viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/></symbol>
		<symbol id="admin-calendar" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/></symbol>
		<symbol id="admin-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>
		<symbol id="admin-money" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M7 9h.01M17 15h.01"/></symbol>
		<symbol id="admin-logout" viewBox="0 0 24 24"><path d="m10 17 5-5-5-5M15 12H3M21 4v16"/></symbol>
		<symbol id="admin-truck" viewBox="0 0 24 24"><path d="M3 6h11v11H3zM14 10h4l3 3v4h-7"/><circle cx="7" cy="19" r="2"/><circle cx="18" cy="19" r="2"/></symbol>
		<symbol id="admin-alert" viewBox="0 0 24 24"><path d="M12 3 22 20H2L12 3ZM12 9v5M12 17h.01"/></symbol>
		<symbol id="admin-gift" viewBox="0 0 24 24"><path d="M3 10h18v11H3zM2 7h20v3H2zM12 7v14M12 7H8.5a2.5 2.5 0 1 1 2.5-2.5V7ZM12 7h3.5A2.5 2.5 0 1 0 13 4.5V7Z"/></symbol>
		<symbol id="admin-copy" viewBox="0 0 24 24"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></symbol>
		<symbol id="admin-download" viewBox="0 0 24 24"><path d="M12 3v12M7 10l5 5 5-5M4 21h16"/></symbol>
		<symbol id="admin-edit" viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z"/></symbol>
		<symbol id="admin-trash" viewBox="0 0 24 24"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 14h10l1-14M9 7V4h6v3"/></symbol>
		<symbol id="admin-close" viewBox="0 0 24 24"><path d="m6 6 12 12M18 6 6 18"/></symbol>
		<symbol id="admin-upload" viewBox="0 0 24 24"><path d="M12 16V4M7 9l5-5 5 5M4 20h16"/></symbol>
		<symbol id="admin-image" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="9" r="1.5"/><path d="m21 16-5-5-6 6-2-2-5 5"/></symbol>
		<symbol id="admin-ban" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="m5.5 5.5 13 13"/></symbol>
		<symbol id="admin-check" viewBox="0 0 24 24"><path d="m5 12 4 4L19 6"/></symbol>
		<symbol id="admin-trend" viewBox="0 0 24 24"><path d="m4 17 6-6 4 4 6-8M15 7h5v5"/></symbol>
		<symbol id="admin-rupee" viewBox="0 0 24 24"><path d="M6 4h12M6 8h12M8 4c4 0 6 2 6 5s-2 5-6 5h-2l8 6"/></symbol>
		<symbol id="admin-wallet" viewBox="0 0 24 24"><path d="M4 6h16v14H4zM4 6V4h14M16 13h5"/><circle cx="16" cy="13" r="1"/></symbol>
		<symbol id="admin-cart" viewBox="0 0 24 24"><path d="M3 4h2l2 12h11l3-8H6"/><circle cx="10" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/></symbol>
		<symbol id="admin-card" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18"/></symbol>
		<symbol id="admin-store" viewBox="0 0 24 24"><path d="M3 10h18M5 10v10h14V10M4 10l2-6h12l2 6M8 20v-6h8v6"/></symbol>
		<symbol id="admin-user" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.5-7 8-7s8 3 8 7"/></symbol>
		<symbol id="admin-security" viewBox="0 0 24 24"><path d="M12 3 20 6v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3Z"/><path d="m9 12 2 2 4-5"/></symbol>
		<symbol id="admin-bell-settings" viewBox="0 0 24 24"><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/></symbol>
		<symbol id="admin-payment" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18"/></symbol>
		<symbol id="admin-palette" viewBox="0 0 24 24"><path d="M12 3a9 9 0 1 0 0 18h2c1 0 1.5-1.5.8-2.2-.7-.7-.2-2.2.8-2.2H18a3 3 0 0 0 3-3C21 7.8 17 3 12 3Z"/><circle cx="7.5" cy="10" r="1"/><circle cx="10" cy="7" r="1"/><circle cx="14" cy="7" r="1"/></symbol>
		<symbol id="admin-maintenance" viewBox="0 0 24 24"><path d="m14 6 4 4M3 21l9-9M15 4a5 5 0 0 0 5 5l-3 3-5-5 3-3ZM4 20l2-2"/></symbol>
		<symbol id="admin-danger" viewBox="0 0 24 24"><path d="M12 3 2 21h20L12 3Z"/><path d="M12 9v5M12 18h.01"/></symbol>
		<symbol id="admin-save" viewBox="0 0 24 24"><path d="M5 3h12l3 3v15H5zM8 3v6h8V3M8 21v-7h8v7"/></symbol>
		<symbol id="admin-arrow-left" viewBox="0 0 24 24"><path d="M19 12H5M11 6l-6 6 6 6"/></symbol>
		<symbol id="admin-print" viewBox="0 0 24 24"><path d="M6 9V3h12v6M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2M6 14h12v7H6z"/></symbol>
		<symbol id="admin-phone" viewBox="0 0 24 24"><path d="M6 3h4l2 5-2 2c1 2 3 3 4 4l2-2 5 2v4c-8 2-15-5-15-15z"/></symbol>
		<symbol id="admin-more" viewBox="0 0 24 24"><circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/></symbol>
		<symbol id="admin-send" viewBox="0 0 24 24"><path d="m21 3-7.5 18-3.5-7-7-3.5L21 3Z"/><path d="m10 14 5-5"/></symbol>
		<symbol id="admin-mail" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M4 7l8 6 8-6"/></symbol>
		<symbol id="admin-location" viewBox="0 0 24 24"><path d="M12 21s7-6 7-12a7 7 0 0 0-14 0c0 6 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></symbol>
		<symbol id="admin-note" viewBox="0 0 24 24"><path d="M5 3h14v18H5zM8 8h8M8 12h8M8 16h5"/></symbol>
		<symbol id="admin-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v6l4 2"/></symbol>
		<symbol id="admin-ip" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></symbol>
	</svg>;
}
