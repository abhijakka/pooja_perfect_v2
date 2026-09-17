"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AdminIcon, AdminIconSprite } from "./AdminIcon";
import { AdminHeader } from "./AdminHeader";
import { AdminSidebar } from "./AdminSidebar";
import { categories, kpis, orders, sales, stockItems, type OrderStatus } from "./dashboard-data";
import { adminApi, type Dashboard } from "../../../services/api/admin.api";

function PanelHeader({ title, subtitle, action }: { title: string; subtitle: string; action?: string }) { return <div className="admin-panel-header"><div><div className="admin-panel-title">{title}</div><div className="admin-panel-subtitle">{subtitle}</div></div>{action && <button className="admin-panel-action" type="button" onClick={() => window.alert(action)}>{action} ▾</button>}</div>; }

export function AdminDashboard() {
	const [sidebarOpen, setSidebarOpen] = useState(false);
	const [query, setQuery] = useState("");
	const router = useRouter();
	const [dashboard, setDashboard] = useState<Dashboard | null>(null);
	useEffect(() => {
		adminApi.getDashboard().then(({ dashboard: result }) => setDashboard(result)).catch(() => undefined);
	}, []);
	useEffect(() => { const close = (event: KeyboardEvent) => event.key === "Escape" && setSidebarOpen(false); document.addEventListener("keydown", close); return () => document.removeEventListener("keydown", close); }, []);
	const dashboardKpis = dashboard ? [
		{ ...kpis[0], value: `₹${dashboard.revenue.toLocaleString("en-IN")}`, growth: `↑ ${dashboard.revenueGrowth}%` },
		{ ...kpis[1], value: dashboard.totalOrders.toLocaleString("en-IN") },
		{ ...kpis[2], value: dashboard.totalCustomers.toLocaleString("en-IN") },
		{ ...kpis[3], value: dashboard.totalProducts.toLocaleString("en-IN") },
	] : kpis;
	const dashboardOrders = dashboard?.recentOrders.map((order) => ({ id: order.orderId, initials: order.customerName.split(" ").map((part) => part[0]).join("").slice(0, 2), name: order.customerName, email: order.customerEmail, date: "", amount: `₹${order.amount.toLocaleString("en-IN")}`, payment: order.paymentMethod, status: order.status, statusKey: order.status.toLowerCase() as OrderStatus })) ?? orders;
	const filteredOrders = dashboardOrders.filter((order) => `${order.id} ${order.name} ${order.email} ${order.status}`.toLowerCase().includes(query.trim().toLowerCase()));
	return <div className="admin-dashboard"><AdminIconSprite /><AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} /><main className="admin-main"><AdminHeader onMenu={() => setSidebarOpen(true)} query={query} onQuery={setQuery} /><div className="admin-content"><section className="admin-welcome"><div><h1>Good afternoon, <span>Admin</span></h1><p>Here&apos;s what&apos;s happening with PoojaPoint today.</p></div><button className="admin-date-button" type="button" onClick={() => window.alert("Date range selector\nToday\nYesterday\nLast 7 days\nLast 30 days\nCustom range")}><AdminIcon name="calendar" />19 Aug 2026</button></section>
		<section className="admin-kpi-grid">{dashboardKpis.map((kpi) => <article className="admin-kpi" key={kpi.label}><div className="admin-kpi-top"><div className="admin-kpi-icon"><AdminIcon name={kpi.icon} /></div><div className={`admin-kpi-growth ${kpi.down ? "down" : ""}`}>{kpi.growth}</div></div><div className="admin-kpi-label">{kpi.label}</div><div className="admin-kpi-value">{kpi.value}</div><div className="admin-kpi-footer">{kpi.footer}</div></article>)}</section>
		<section className="admin-dashboard-grid"><div className="admin-panel"><PanelHeader title="Sales Overview" subtitle="Revenue performance" action="Last 7 months" /><div className="admin-chart-body"><div className="admin-chart-summary"><div><div className="admin-chart-total">₹4.82L</div><div className="admin-chart-change">+12.8% from previous period</div></div></div><div className="admin-chart">{[25, 50, 75].map((line) => <div className="admin-chart-grid-line" style={{ top: `${line}%` }} key={line} />)}{sales.map((item, index) => <div className="admin-bar-group" key={item.month}><div className={`admin-bar ${index === sales.length - 1 ? "main-bar" : ""}`} style={{ height: `${item.value}%` }} /><span>{item.month}</span></div>)}</div><div className="admin-mini-stats">{[["Avg. Order Value", "₹1,842"], ["Conversion", "4.82%"], ["Refunds", "1.4%"]].map(([label, value]) => <div className="admin-mini-stat" key={label}><div>{label}</div><strong>{value}</strong></div>)}</div></div></div>
			<div className="admin-panel"><PanelHeader title="Top Categories" subtitle="Sales by category" /><div className="admin-category-list">{categories.map((category) => <div className="admin-category" key={category.name}><div className="admin-category-icon"><AdminIcon name={category.icon} /></div><div className="admin-category-info"><div className="admin-category-name">{category.name}</div><div className="admin-category-count">{category.count}</div></div><div className="admin-category-sales">{category.sales}</div></div>)}</div></div></section>
		<section className="admin-panel admin-orders-panel"><PanelHeader title="Recent Orders" subtitle="Latest customer purchases" action="View all orders" /><div className="admin-table-wrap"><table className="admin-orders-table"><thead><tr>{["Order", "Customer", "Date", "Amount", "Payment", "Status"].map((heading) => <th key={heading}>{heading}</th>)}</tr></thead><tbody>{filteredOrders.map((order) => <tr key={order.id}><td><span className="admin-order-id">{order.id}</span></td><td><div className="admin-customer"><div className="admin-customer-avatar">{order.initials}</div><div><div className="admin-customer-name">{order.name}</div><div className="admin-customer-email">{order.email}</div></div></div></td><td>{order.date}</td><td><span className="admin-amount">{order.amount}</span></td><td>{order.payment}</td><td><span className={`admin-order-status ${order.statusKey}`}>{order.status}</span></td></tr>)}</tbody></table>{filteredOrders.length === 0 && <p className="admin-empty">No matching orders.</p>}</div></section>
		<section className="admin-bottom-grid"><div className="admin-panel"><PanelHeader title="Low Stock Alerts" subtitle="Products requiring attention" /><div className="admin-stock-list">{stockItems.map((item) => <div className="admin-stock-item" key={item.sku}><div className="admin-stock-image"><AdminIcon name={item.icon} /></div><div className="admin-stock-info"><div>{item.name}</div><small>{item.sku}</small></div><div className="admin-stock-count"><strong>{item.count}</strong><small>left</small></div></div>)}</div></div><div className="admin-panel"><PanelHeader title="Quick Actions" subtitle="Frequently used tools" /><div className="admin-quick-actions">{[["plus", "Add Product", "Create new product", "/admin/products"], ["orders", "Manage Orders", "Process pending orders", "/admin/orders"], ["discount", "Create Coupon", "Add promotional offer", "/admin/coupons"], ["analytics", "Sales Report", "View store performance", "/admin/reports"]].map(([icon, title, text, href]) => <button className="admin-quick-action" type="button" key={title} onClick={() => router.push(href)}><span className="admin-quick-action-icon"><AdminIcon name={icon as "plus" | "orders" | "discount" | "analytics"} /></span><span><strong>{title}</strong><small>{text}</small></span></button>)}</div></div></section>
		</div></main></div>;
}
