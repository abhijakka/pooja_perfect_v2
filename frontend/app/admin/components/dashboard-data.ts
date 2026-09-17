export type IconName =
	| "ai"
	| "analytics"
	| "alert"
	| "bell"
	| "ban"
	| "calendar"
	| "check"
	| "close"
	| "copy"
	| "download"
	| "discount"
	| "edit"
	| "category"
	| "customers"
	| "discount"
	| "eye"
	| "gift"
	| "grid"
	| "image"
	| "logo"
	| "logout"
	| "menu"
	| "money"
	| "orders"
	| "plus"
	| "products"
	| "review"
	| "search"
	| "settings"
	| "trash"
	| "trend"
	| "truck"
	| "upload"
	| "rupee"
	| "wallet"
	| "cart"
	| "card"
	| "chat"
	| "more"
	| "send"
	| "arrow-left"
	| "print"
	| "phone"
	| "mail"
	| "location"
	| "note"
	| "clock"
	| "ip"
	| "store"
	| "user"
	| "security"
	| "bell-settings"
	| "payment"
	| "palette"
	| "maintenance"
	| "danger"
	| "save"
	| "wishlist";

export type OrderStatus = "delivered" | "processing" | "shipped" | "cancelled";

export const kpis = [
	{ label: "Total Revenue", value: "₹4,82,590", footer: "Compared with last month", growth: "↑ 12.8%", icon: "money" as IconName },
	{ label: "Total Orders", value: "1,284", footer: "12 orders need attention", growth: "↑ 8.4%", icon: "orders" as IconName },
	{ label: "Customers", value: "8,492", footer: "186 new this month", growth: "↑ 5.6%", icon: "customers" as IconName },
	{ label: "Products", value: "428", footer: "421 active products", growth: "7 low stock", icon: "products" as IconName, down: true },
];

export const sales = [
	{ month: "Feb", value: 48 }, { month: "Mar", value: 60 }, { month: "Apr", value: 54 },
	{ month: "May", value: 72 }, { month: "Jun", value: 66 }, { month: "Jul", value: 82 }, { month: "Aug", value: 94 },
];

export const categories = [
	{ name: "Pooja Products", count: "184 products", sales: "₹2.14L", icon: "logo" as IconName },
	{ name: "Silver", count: "96 products", sales: "₹1.26L", icon: "products" as IconName },
	{ name: "Decorate Products", count: "73 products", sales: "₹82K", icon: "category" as IconName },
	{ name: "Festival Specials", count: "42 products", sales: "₹61K", icon: "gift" as IconName },
];

export const orders = [
	{ id: "#PP102834", initials: "AK", name: "Abhinav Kumar", email: "abhinav@example.com", date: "19 Aug 2026", amount: "₹1,859", payment: "UPI", status: "Delivered", statusKey: "delivered" as OrderStatus },
	{ id: "#PP102833", initials: "RS", name: "Riya Sharma", email: "riya@example.com", date: "19 Aug 2026", amount: "₹2,499", payment: "Card", status: "Processing", statusKey: "processing" as OrderStatus },
	{ id: "#PP102832", initials: "SM", name: "Suresh Mehta", email: "suresh@example.com", date: "18 Aug 2026", amount: "₹899", payment: "UPI", status: "Shipped", statusKey: "shipped" as OrderStatus },
	{ id: "#PP102831", initials: "PM", name: "Priya Menon", email: "priya@example.com", date: "18 Aug 2026", amount: "₹1,299", payment: "COD", status: "Processing", statusKey: "processing" as OrderStatus },
	{ id: "#PP102830", initials: "VN", name: "Vinay Nair", email: "vinay@example.com", date: "17 Aug 2026", amount: "₹649", payment: "Card", status: "Cancelled", statusKey: "cancelled" as OrderStatus },
];

export const stockItems = [
	{ name: "Brass Diya Premium", sku: "PP-DIYA-001", count: 4, icon: "logo" as IconName },
	{ name: "Silver Pooja Coin", sku: "PP-SIL-028", count: 7, icon: "products" as IconName },
	{ name: "Premium Pooja Thali", sku: "PP-THALI-012", count: 3, icon: "category" as IconName },
	{ name: "Kumkum Haldi Set", sku: "PP-KH-003", count: 6, icon: "logo" as IconName },
];
