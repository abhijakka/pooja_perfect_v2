"use client";

import { useState } from "react";
import Link from "next/link";
import { AdminHeader } from "./AdminHeader";
import { AdminIcon, AdminIconSprite } from "./AdminIcon";
import { AdminSidebar } from "./AdminSidebar";

const orderItems = [
	["Premium Brass Pooja Diya", "PP-DIYA-001", "Qty: 1 · Brass", "₹349"],
	["Kumkum & Pasupu Combo", "PP-KP-002", "Qty: 2 · Pooja Essential", "₹198"],
	["Fresh Pooja Flowers", "PP-FLOWER-250", "Qty: 1 · 250 gms", "₹79"],
] as const;
const timeline = [
	["Order Placed", "Order successfully received by PoojaPoint.", "10:42 AM", "check"],
	["Payment Confirmed", "Payment received successfully.", "10:43 AM", "check"],
	["Order Accepted", "Store team accepted the order for preparation.", "10:48 AM", "check"],
	["Preparing", "Products are waiting to be prepared and packed.", "Pending", "clock"],
	["Out for Delivery", "Delivery partner will receive the package.", "Pending", "truck"],
	["Delivered", "Order delivered to the customer.", "Pending", "check"],
] as const;
const statusOptions = ["processing", "accepted", "preparing", "packed", "shipped", "delivered", "cancelled"];
const statusName = (value: string) => value === "shipped" ? "On the Way" : value[0].toUpperCase() + value.slice(1);

function Panel({ title, subtitle, children, action }: { title: string; subtitle: string; children: React.ReactNode; action?: React.ReactNode }) {
	return <section className="order-detail-exact-panel"><header><div><h2>{title}</h2><p>{subtitle}</p></div>{action}</header><div className="order-detail-exact-body">{children}</div></section>;
}

export function AdminOrderDetailPage({ orderId }: { orderId: string }) {
	const [sidebarOpen, setSidebarOpen] = useState(false);
	const [status, setStatus] = useState("processing");
	const [note, setNote] = useState("");
	const [toast, setToast] = useState("");
	const notify = (message: string) => { setToast(message); window.setTimeout(() => setToast(""), 2400); };
	return <div className="admin-dashboard">
		<AdminIconSprite /><AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} activeHref="/admin/orders" />
		<main className="admin-main"><AdminHeader onMenu={() => setSidebarOpen(true)} query="" onQuery={() => undefined} title="Order Detail" subtitle="View and manage individual order information" />
		<div className="admin-content"><div className="order-detail-exact-page">
			<div className="order-detail-exact-breadcrumb"><Link href="/admin/orders">Orders</Link><span>›</span><strong>#{orderId}</strong></div>
			<div className="order-detail-exact-top"><div className="order-detail-exact-heading"><Link href="/admin/orders" aria-label="Back to orders"><AdminIcon name="arrow-left" /></Link><div><h1>Order #{orderId}</h1><p>Placed on 20 August 2026 at 10:42 AM</p></div></div><div className="order-detail-exact-actions"><button type="button" onClick={() => window.print()}><AdminIcon name="print" />Print</button><button type="button" onClick={() => notify("Invoice generation started.")}><AdminIcon name="download" />Invoice</button><button className="danger" type="button" onClick={() => { setStatus("cancelled"); notify("Order marked for cancellation."); }}>Cancel Order</button></div></div>
			<div className="order-detail-exact-status-row"><span className="processing"><i />{statusName(status)}</span><span className="paid"><i />Payment Paid</span><span className="info"><AdminIcon name="calendar" />Subscription Order</span></div>
			<div className="order-detail-exact-grid"><div className="order-detail-exact-stack">
				<Panel title="Order Items" subtitle="Products included in this order" action={<span>3 Items</span>}><>{orderItems.map(([name, sku, meta, price]) => <div className="order-detail-exact-item" key={sku}><div className="order-detail-exact-product-image"><AdminIcon name="products" /></div><div><strong>{name}</strong><small>SKU: {sku}</small><em>{meta}</em></div><aside><strong>{price}</strong><small>{price} × 1</small></aside></div>)}<div className="order-detail-exact-summary"><p><span>Subtotal</span><strong>₹626</strong></p><p><span>Delivery Fee</span><strong>₹30</strong></p><p className="discount"><span>Subscription Discount</span><strong>− ₹56</strong></p><p><span>Tax</span><strong>₹30</strong></p><p className="total"><span>Grand Total</span><strong>₹630</strong></p></div></></Panel>
				<Panel title="Delivery Information" subtitle="Schedule and address for this order" action={<span className="info">6:00 AM – 9:00 AM</span>}><div className="order-detail-exact-info-grid"><div><label>Delivery Date</label><strong>21 August 2026</strong><small>Friday</small></div><div><label>Delivery Window</label><strong>Early Morning</strong><small>6:00 AM – 9:00 AM</small></div></div><div className="order-detail-exact-detail"><AdminIcon name="location" /><div><label>Delivery Address</label><p>Abhinav Kumar<br />Flat 402, Sri Sai Residency<br />Madhapur, Hyderabad, Telangana<br />500081, India</p></div></div></Panel>
				<Panel title="Order Timeline" subtitle="Order processing history"><div className="order-detail-exact-timeline">{timeline.map(([title, text, time, icon], index) => <div key={title}><i className={index < 3 ? "done" : ""}><AdminIcon name={icon as "check" | "clock" | "truck"} /></i><span><strong>{title}</strong><small>{text}</small></span><em>{time}</em></div>)}</div></Panel>
				<Panel title="Customer Note" subtitle="Message provided during checkout"><div className="order-detail-exact-note">Please deliver the pooja items before 9:00 AM. If the customer is unavailable, please call before leaving the package.</div></Panel>
			</div><div className="order-detail-exact-stack">
				<Panel title="Customer" subtitle="Customer information" action={<Link href="/admin/customers">View Customer</Link>}><div className="order-detail-exact-customer"><div>AK</div><span><strong>Abhinav Kumar</strong><small>Customer since June 2026</small></span></div>{[["mail", "Email", "abhinav@example.com"], ["phone", "Phone", "+91 98765 43210"]].map(([icon, label, value]) => <div className="order-detail-exact-detail" key={label}><AdminIcon name={icon as "mail" | "phone"} /><div><label>{label}</label><p>{value}</p></div></div>)}</Panel>
				<Panel title="Payment" subtitle="Transaction information" action={<span className="paid">Paid</span>}>{[["card", "Payment Method", "UPI"], ["rupee", "Amount Paid", "₹630"], ["note", "Transaction ID", "TXN_PPG_10248_2026"], ["calendar", "Paid On", "20 Aug 2026 · 10:43 AM"]].map(([icon, label, value]) => <div className="order-detail-exact-detail" key={label}><AdminIcon name={icon as "card" | "rupee" | "note" | "calendar"} /><div><label>{label}</label><p>{value}</p></div></div>)}</Panel>
				<Panel title="Subscription" subtitle="Recurring delivery plan" action={<span className="info">Monthly</span>}><div className="order-detail-exact-info-grid"><div><label>Plan</label><strong>1 Month · 1 Day</strong><small>One delivery day every week.</small></div><div><label>Delivery Day</label><strong>Friday</strong><small>Repeats during subscription.</small></div></div><div className="order-detail-exact-detail"><AdminIcon name="calendar" /><div><label>Subscription Period</label><p>21 Aug 2026 – 20 Sep 2026</p></div></div><div className="order-detail-exact-detail"><AdminIcon name="clock" /><div><label>Preferred Delivery Time</label><p>6:00 AM – 9:00 AM</p></div></div></Panel>
				<Panel title="Manage Order" subtitle="Update order status"><div className="order-detail-exact-control"><label>Order Status</label><select value={status} onChange={(event) => setStatus(event.target.value)}>{statusOptions.map((option) => <option value={option} key={option}>{statusName(option)}</option>)}</select><label>Internal Note</label><textarea value={note} onChange={(event) => setNote(event.target.value)} placeholder="Add an internal note..." /><button type="button" onClick={() => notify(`Order updated: ${statusName(status)}`)}>Save Order Update</button></div></Panel>
			</div></div>
		</div></div></main>{toast && <div className="coupon-exact-toast show">{toast}</div>}
	</div>;
}
