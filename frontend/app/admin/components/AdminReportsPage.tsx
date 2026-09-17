"use client";

import { useState } from "react";
import { AdminHeader } from "./AdminHeader";
import { AdminIcon, AdminIconSprite } from "./AdminIcon";
import { AdminSidebar } from "./AdminSidebar";
import { adminApi } from "../../../services/api/admin.api";

type ReportType = "sales" | "orders" | "customers" | "products" | "subscriptions" | "inventory" | "payments" | "coupons";
type Report = { type: ReportType; period: string; generated: string; records: string };

const reportCards: Array<[ReportType, string, string, "rupee" | "orders" | "customers" | "products" | "analytics" | "category" | "card" | "discount"]> = [
	["sales", "Sales Report", "Revenue, discounts, refunds and net sales.", "rupee"],
	["orders", "Orders Report", "Orders, customers, items, payment and status.", "orders"],
	["customers", "Customer Report", "Customers, orders, spending and activity.", "customers"],
	["products", "Product Report", "Product sales, revenue and stock movement.", "products"],
	["subscriptions", "Subscription Report", "Daily, monthly and Pay As You Go subscriptions.", "analytics"],
	["inventory", "Inventory Report", "Stock, low stock, out of stock and stock value.", "category"],
	["payments", "Payment Report", "UPI, cards, wallets, COD and payment status.", "card"],
	["coupons", "Coupon Report", "Coupon usage, discounts and redemptions.", "discount"],
];
const typeName = (type: ReportType) => `${type[0].toUpperCase()}${type.slice(1)} Report`;
const defaultToDate = new Date();
const defaultFromDate = new Date(defaultToDate);
defaultFromDate.setDate(defaultToDate.getDate() - 29);
const isoDate = (date: Date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;

export function AdminReportsPage() {
	const [sidebarOpen, setSidebarOpen] = useState(false);
	const [period, setPeriod] = useState("30");
	const [reportType, setReportType] = useState<ReportType>("sales");
	const [fromDate, setFromDate] = useState(isoDate(defaultFromDate));
	const [toDate, setToDate] = useState(isoDate(defaultToDate));
	const [reportStatus, setReportStatus] = useState("all");
	const [category, setCategory] = useState("all");
	const [selectedCard, setSelectedCard] = useState<ReportType>("sales");
	const [recentReports, setRecentReports] = useState<Report[]>([]);
	const [toast, setToast] = useState("");
	const notify = (message: string) => { setToast(message); window.setTimeout(() => setToast(""), 2300); };
	const formatDate = (date: Date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
	const applyPeriod = (value: string) => { setPeriod(value); const to = new Date(); const from = new Date(); if (value === "today") from.setHours(0, 0, 0, 0); else from.setDate(to.getDate() - Number(value) + 1); setFromDate(formatDate(from)); setToDate(formatDate(to)); };
	const generateReport = async () => { if (fromDate && toDate && fromDate > toDate) { notify("From date cannot be after To date."); return; } try { const { report } = await adminApi.getReport(reportType, fromDate || undefined, toDate || undefined); setRecentReports((current) => [{ type: reportType, period: `${fromDate} – ${toDate}`, generated: report.generatedAt, records: String(report.data.length) }, ...current]); notify(`${report.name} generated`); } catch { notify("Report could not be generated"); } };
	const downloadReport = (type: ReportType) => notify(`Report download is not available from the backend yet: ${type}`);
	const exportCurrent = () => downloadReport(reportType);

	return <div className="admin-dashboard"><AdminIconSprite /><AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} activeHref="/admin/reports" /><main className="admin-main"><AdminHeader onMenu={() => setSidebarOpen(true)} query="" onQuery={() => undefined} title="Reports" subtitle="Generate and review PoojaPoint store reports" /><div className="admin-content"><div className="reports-exact-page"><div className="reports-exact-top"><div><div className="reports-exact-heading">Reports</div><div className="reports-exact-description">Generate, filter and export reports for your PoojaPoint store.</div></div><div className="reports-exact-actions"><select value={period} onChange={(event) => applyPeriod(event.target.value)}><option value="today">Today</option><option value="7">Last 7 days</option><option value="30">Last 30 days</option><option value="90">Last 90 days</option><option value="365">This year</option></select><button type="button" onClick={generateReport}><AdminIcon name="download" />Generate Report</button></div></div><section className="reports-exact-kpis">{[["rupee", "TOTAL REVENUE", "₹8,42,680", "Revenue"], ["orders", "TOTAL ORDERS", "1,284", "Orders"], ["customers", "CUSTOMERS", "968", "Customers"], ["products", "PRODUCTS SOLD", "3,742", "Products"]].map(([icon, label, value, change]) => <article key={label}><div className="reports-exact-kpi-top"><div className="reports-exact-kpi-icon"><AdminIcon name={icon as "rupee" | "orders" | "customers" | "products"} /></div><span>{change}</span></div><div className="reports-exact-kpi-label">{label}</div><strong>{value}</strong><small>Selected reporting period</small></article>)}</section><section className="admin-panel reports-exact-panel"><div className="reports-exact-panel-header"><div><div className="reports-exact-panel-title">Report Center</div><div className="reports-exact-panel-subtitle">Choose the report you want to generate.</div></div></div><div className="reports-exact-report-grid">{reportCards.map(([type, title, description, icon]) => <button className={selectedCard === type ? "selected" : ""} type="button" key={type} onClick={() => { setSelectedCard(type); setReportType(type); notify(`${title} selected`); }}><div className="reports-exact-report-icon"><AdminIcon name={icon} /></div><div><strong>{title}</strong><span>{description}</span></div></button>)}</div></section><section className="admin-panel reports-exact-panel"><div className="reports-exact-panel-header"><div><div className="reports-exact-panel-title">Report Filters</div><div className="reports-exact-panel-subtitle">Select the exact data you want in the report.</div></div></div><div className="reports-exact-filter-grid"><label>Report Type<select value={reportType} onChange={(event) => setReportType(event.target.value as ReportType)}>{reportCards.map(([type, title]) => <option value={type} key={type}>{title}</option>)}</select></label><label>From Date<input type="date" value={fromDate} onChange={(event) => setFromDate(event.target.value)} /></label><label>To Date<input type="date" value={toDate} onChange={(event) => setToDate(event.target.value)} /></label><label>Status<select value={reportStatus} onChange={(event) => setReportStatus(event.target.value)}><option value="all">All Statuses</option><option value="completed">Completed</option><option value="processing">Processing</option><option value="shipped">On the Way</option><option value="delivered">Delivered</option><option value="cancelled">Cancelled</option></select></label><label>Category<select value={category} onChange={(event) => setCategory(event.target.value)}><option value="all">All Categories</option><option>Pooja Products</option><option>Silver</option><option>Decorate Products</option><option>Pooja Gifts</option></select></label><button type="button" onClick={generateReport}><AdminIcon name="download" />Generate Report</button></div></section><section className="admin-panel reports-exact-panel reports-exact-recent"><div className="reports-exact-panel-header"><div><div className="reports-exact-panel-title">Recent Reports</div><div className="reports-exact-panel-subtitle">Previously generated reports.</div></div><button type="button" onClick={() => { setRecentReports([]); notify("Recent reports cleared"); }}>Clear</button></div><div className="admin-table-wrap"><table><thead><tr>{["Report", "Period", "Generated", "Records", "Format", "Status", "Action"].map((heading) => <th key={heading}>{heading}</th>)}</tr></thead><tbody>{recentReports.length ? recentReports.map((report, index) => <tr key={`${report.type}-${index}`}><td>{typeName(report.type)}</td><td>{report.period}</td><td>{report.generated}</td><td>{report.records}</td><td>CSV</td><td><span>Ready</span></td><td><button type="button" onClick={() => downloadReport(report.type)}>Download</button></td></tr>) : <tr><td colSpan={7}>No generated reports.</td></tr>}</tbody></table></div></section><section className="reports-exact-insights">{[["trend", "Finance reports", "Use Sales and Payment reports for revenue reconciliation."], ["products", "Inventory reports", "Track stock, low-stock products and inventory value."], ["customers", "Customer reports", "Review customer activity and subscription performance."]].map(([icon, title, text]) => <article key={title}><div><AdminIcon name={icon as "trend" | "products" | "customers"} /></div><section><strong>{title}</strong><span>{text}</span></section></article>)}</section></div></div></main>{toast && <div className="coupon-exact-toast show">{toast}</div>}</div>;
}
