"use client";

import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Icon } from "../../../components/Icon";
import { PublicFooter } from "../../../components/layout/PublicFooter/PublicFooter";
import { PublicHeader } from "../../../components/layout/PublicHeader/PublicHeader";
import { useCart } from "../../../hooks/useCart";
import { useWishlist } from "../../../hooks/useWishlist";
import { products, type Product } from "../../(public)/storefront-data";
import { accountApi, type AccountOrder } from "../../../services/api/account.api";

type OrderStatus = "processing" | "transit" | "delivered" | "cancelled";
type OrderProduct = { id?: string; name: string; quantity: number; price: number; image?: string; category: string };
type OrderRecord = { id: string; date: string; total: number; status: OrderStatus; statusLabel: string; deliveryTitle: string; deliveryText: string; message: string; items: OrderProduct[] };

const filters: Array<["all" | OrderStatus, string]> = [["all", "All Orders"], ["processing", "Processing"], ["transit", "On the way"], ["delivered", "Delivered"], ["cancelled", "Cancelled"]];

function money(value: number) {
	return `₹${value.toLocaleString("en-IN")}`;
}

function resolveProduct(item: OrderProduct, index: number): Product | null {
	return item.id ? products.find((product) => product.id === item.id) ?? null : products[index % products.length] ?? null;
}

export default function OrdersPage() {
	const router = useRouter();
	const { count: cartCount, addItem } = useCart();
	const { count: wishlistCount } = useWishlist();
	const [query, setQuery] = useState("");
	const [filter, setFilter] = useState<"all" | OrderStatus>("all");
	const [cancelled, setCancelled] = useState<string[]>([]);
	const [ratings, setRatings] = useState<Record<string, number>>({});
	const [orderData, setOrderData] = useState<OrderRecord[]>([]);
	const [toast, setToast] = useState("");
	const [nav, setNav] = useState("orders");
	useEffect(() => {
		accountApi.getOverview().then(({ orders }) => setOrderData(orders.items.map((order: AccountOrder) => {
			const status = order.status.toLowerCase();
			const normalized: OrderStatus = status.includes("cancel") ? "cancelled" : status.includes("deliver") ? "delivered" : status.includes("ship") || status.includes("transit") ? "transit" : "processing";
			return { id: order.orderNumber, date: new Date(order.createdAt).toLocaleDateString("en-IN"), total: Number(order.total), status: normalized, statusLabel: order.status, deliveryTitle: order.status, deliveryText: order.status, message: order.status, items: order.items.map((item) => ({ id: item.productId, name: item.productName, quantity: item.quantity, price: Number(item.unitPrice), category: "Pooja Essentials" })) };
		}))).catch(() => setToast("Orders could not be loaded"));
	}, []);
	const suggestions = useMemo(() => query ? products.filter((item) => `${item.name} ${item.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : [], [query]);
	const visibleOrders = useMemo(() => orderData.filter((order) => {
		const status = cancelled.includes(order.id) ? "cancelled" : order.status;
		const searchable = `${order.id} ${order.items.map((item) => item.name).join(" ")}`.toLowerCase();
		return (filter === "all" || status === filter) && (!query.trim() || searchable.includes(query.trim().toLowerCase()));
	}), [cancelled, filter, orderData, query]);

	const notify = (message: string) => {
		setToast(message);
		window.setTimeout(() => setToast(""), 2200);
	};
	const submitSearch = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		if (!query.trim()) notify("Type an order ID or product name");
	};
	const buyAgain = (order: OrderRecord) => {
		order.items.forEach((item, index) => {
			const product = resolveProduct(item, index);
			if (product) addItem(product, item.quantity);
		});
		notify("Previous items added to cart");
		window.setTimeout(() => router.push("/cart"), 500);
	};
	const cancelOrder = (order: OrderRecord) => {
		if (!window.confirm(`Are you sure you want to cancel order ${order.id}?`)) return;
		setCancelled((current) => current.includes(order.id) ? current : [...current, order.id]);
		notify("Cancellation request submitted");
	};

	return <>
		<PublicHeader query={query} suggestions={suggestions} cartCount={cartCount} wishlistCount={wishlistCount} onQueryChange={setQuery} onSearch={submitSearch} onProfile={() => notify("Profile opened")} onWishlist={() => router.push("/wishlist")} onCart={() => router.push("/cart")} />
		<main className="my-orders-page">
			<div className="breadcrumb"><Link href="/">Home</Link><span>›</span>My Orders</div>
			<header className="orders-page-header"><div><div className="orders-eyebrow">Your PoojaPoint</div><h1>My Orders</h1><p>View, track and manage all your PoojaPoint purchases in one place.</p></div><Link href="/products" className="orders-shop-button">Continue Shopping</Link></header>
			<section className="orders-toolbar"><div className="orders-tabs">{filters.map(([value, label]) => <button className={`orders-tab ${filter === value ? "active" : ""}`} onClick={() => setFilter(value)} key={value}>{label}</button>)}</div><form className="orders-search" onSubmit={submitSearch}><Icon name="search" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search order..." aria-label="Search orders" /></form></section>
			<div className="orders-count">Showing {visibleOrders.length} {visibleOrders.length === 1 ? "order" : "orders"}</div>
			<section>{visibleOrders.map((order) => { const currentStatus = cancelled.includes(order.id) ? "cancelled" : order.status; return <article className="order-history-card" key={order.id}><div className="order-history-header"><div className="order-meta"><div><span>Order ID</span><strong>{order.id}</strong></div><div><span>Ordered</span><strong>{order.date}</strong></div><div><span>Total</span><strong>{money(order.total)}</strong></div></div><div className={`order-status ${currentStatus}`}><i />{currentStatus === "cancelled" ? "Cancelled" : order.statusLabel}</div></div><div className="order-history-body"><div className="order-delivery-row"><div className="order-delivery-info"><div className="order-delivery-icon"><Icon name={currentStatus === "transit" ? "truck" : currentStatus === "delivered" ? "check" : "box"} /></div><div><strong>{currentStatus === "cancelled" ? "Order cancelled" : order.deliveryTitle}</strong><span>{currentStatus === "cancelled" ? "Refund processed" : order.deliveryText}</span></div></div><div className="order-total-text">{money(order.total)}<span>{order.items.reduce((total, item) => total + item.quantity, 0)} items</span></div></div><div className="order-products">{order.items.map((item, index) => { const product = resolveProduct(item, index); return <div className="order-product" key={item.name}><div className="order-product-image">{product ? <img src={product.image} alt={item.name} /> : <Icon name="box" />}</div><div className="order-product-info"><strong>{item.name}</strong><span>Qty {item.quantity} · {money(item.price)}</span></div></div>; })}</div>{currentStatus === "delivered" && <div className="order-rating"><span>How was your order?</span><div>{[1, 2, 3, 4, 5].map((value) => <button className={ratings[order.id] >= value ? "selected" : ""} onClick={() => { setRatings((current) => ({ ...current, [order.id]: value })); notify("Thanks for your rating"); }} aria-label={`Rate ${value} stars`} key={value}>★</button>)}</div></div>}<div className="order-history-footer"><p>{order.message}</p><div className="order-actions">{currentStatus === "transit" || currentStatus === "processing" ? <Link href={`/order/track?order=${order.id}`} className="order-action primary">Track Order</Link> : <button className="order-action primary" onClick={() => buyAgain(order)}>Buy Again</button>}{currentStatus !== "cancelled" && <>{currentStatus === "delivered" && <button className="order-action secondary" onClick={() => router.push("/order/confirmation")}>View Details</button>}{currentStatus === "processing" && <button className="order-action danger" onClick={() => cancelOrder(order)}>Cancel</button>}{currentStatus === "transit" && <button className="order-action secondary" onClick={() => router.push("/order/confirmation")}>View Details</button>}</>}{currentStatus === "cancelled" && <button className="order-action secondary" onClick={() => router.push("/order/confirmation")}>Details</button>}</div></div></div></article>; })}</section>
			{!visibleOrders.length && <section className="orders-empty"><div><Icon name="box" /></div><h2>No orders found</h2><p>We could not find any orders matching your search. Try another order ID or explore our latest pooja essentials.</p><Link href="/products" className="orders-empty-button">Start Shopping</Link></section>}
			<section className="orders-help"><div><h2>Need help with an order?</h2><p>Our support team is here to help with delivery, returns, refunds, payments and anything else you need.</p></div><a href="mailto:support@poojapoint.com">Contact Support</a></section>
		</main>
		<PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={cartCount} onNavChange={setNav} onWishlist={() => router.push("/wishlist")} onProfile={() => notify("Profile opened")} />
		{toast && <div className="toast show">{toast}</div>}
	</>;
}
