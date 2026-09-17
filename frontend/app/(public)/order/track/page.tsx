"use client";

import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Icon } from "../../../../components/Icon";
import { PublicFooter } from "../../../../components/layout/PublicFooter/PublicFooter";
import { PublicHeader } from "../../../../components/layout/PublicHeader/PublicHeader";
import { useCart } from "../../../../hooks/useCart";
import { useWishlist } from "../../../../hooks/useWishlist";
import { products } from "../../storefront-data";

const demoOrderId = "PP202608190001";
const demoItems = [
  { productId: "diya", quantity: 1 },
  { productId: "thali", quantity: 1 },
] as const;
const timeline = [
  ["check", "Confirmed", "Aug 19 · 10:15 AM", "completed"],
  ["box", "Packed", "Aug 20 · 9:20 AM", "completed"],
  ["truck", "Out for delivery", "Aug 23 · 8:10 AM", "current"],
  ["location", "Delivered", "Expected Aug 23–25", ""],
] as const;
const activity = [
  ["truck", "Out for delivery", "Your package is with the delivery partner and should reach you today.", "8:10 AM"],
  ["truck", "Shipment reached local hub", "Your package arrived at the local delivery facility.", "Aug 22"],
  ["box", "Package shipped", "Your order has left our fulfilment centre.", "Aug 21"],
  ["check", "Order confirmed", "We have received your order and started preparing it.", "Aug 19"],
] as const;

function money(value: number) {
  return `₹${value.toLocaleString("en-IN")}`;
}

export default function TrackPage() {
  const router = useRouter();
  const { items: cartItems, count: cartCount } = useCart();
  const { count: wishlistCount } = useWishlist();
  const [query, setQuery] = useState("");
  const [orderId, setOrderId] = useState(demoOrderId);
  const [toast, setToast] = useState("");
  const [nav, setNav] = useState("orders");
  const suggestions = useMemo(() => query ? products.filter((item) => `${item.name} ${item.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : [], [query]);
  const orderItems = cartItems.length ? cartItems : demoItems.map(({ productId, quantity }) => ({ ...products.find((product) => product.id === productId)!, quantity }));
  const subtotal = orderItems.reduce((total, item) => total + item.price * item.quantity, 0);

  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2200);
  };
  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const value = orderId.trim().toUpperCase();
    if (!value) return notify("Please enter your order ID");
    if (!value.startsWith("PP")) return notify("Please enter a valid PoojaPoint order ID");
    setOrderId(value);
    notify("Order details loaded");
  };

  return <>
    <PublicHeader query={query} suggestions={suggestions} cartCount={cartCount} wishlistCount={wishlistCount} onQueryChange={setQuery} onSearch={submitSearch} onProfile={() => notify("Profile opened")} onWishlist={() => router.push("/wishlist")} onCart={() => router.push("/cart")} />
    <main className="track-order-page">
      <div className="breadcrumb"><Link href="/">Home</Link><span>›</span><Link href="/order/confirmation">My Order</Link><span>›</span>Track Order</div>
      <header className="track-page-header"><div className="track-eyebrow">PoojaPoint Delivery</div><h1>Track your order</h1><p>Follow your order from our hands to your doorstep. We will keep you updated along the way.</p></header>
      <form className="track-search-card" onSubmit={submitSearch}><label htmlFor="order-id">Enter your order ID</label><div className="track-search-row"><input id="order-id" value={orderId} onChange={(event) => setOrderId(event.target.value)} placeholder="Example: PP202608190001" /><button type="submit">Track Order</button></div><p>Your order ID can be found in your order confirmation email or SMS.</p></form>
      <section className="tracking-card"><div className="tracking-top"><div className="order-info"><small>Order details</small><h2>{orderId}</h2><p>Placed on August 19, 2026 · {orderItems.length} items</p></div><div className="current-status">● Out for delivery</div></div><div className="delivery-estimate"><div className="estimate-left"><div className="estimate-icon"><Icon name="truck" /></div><div><strong>Estimated delivery</strong><span>Your package is on its way</span></div></div><div className="estimate-date">Aug 23 – Aug 25</div></div><div className="tracking-timeline"><div className="timeline-line" /><div className="timeline-progress" />{timeline.map(([icon, title, date, state]) => <div className={`track-step ${state}`} key={title}><div className="step-circle"><Icon name={icon} /></div><div><div className="step-title">{title}</div><div className="step-date">{date}</div></div></div>)}</div></section>
      <section className="track-content-grid"><div><div className="track-card"><div className="track-card-title"><h3>Items in this order</h3><span>{orderItems.length} products</span></div>{orderItems.map((item) => <div className="track-product" key={item.id}><div className="track-product-image"><img src={item.image} alt={item.name} /></div><div className="track-product-info"><strong>{item.name}</strong><span>Qty {item.quantity} · {item.categoryLabel}</span></div><div className="track-product-price">{money(item.price * item.quantity)}</div></div>)}</div><div className="track-card track-activity-card"><div className="track-card-title"><h3>Shipment activity</h3><span>Latest updates</span></div><div className="activity">{activity.map(([icon, title, text, time], index) => <div className={`activity-item ${index === 0 ? "latest" : ""}`} key={title}><div className="activity-dot"><Icon name={icon} /></div><div className="activity-info"><strong>{title}</strong><span>{text}</span></div><div className="activity-time">{time}</div></div>)}</div></div><div className="track-card track-address-card"><div className="track-card-title"><h3>Delivery address</h3><span>Shipping</span></div><div className="track-address"><div className="track-address-icon"><Icon name="location" /></div><div><strong>Abhinav</strong><p>12-45/3, Example Street,<br />Hyderabad, Telangana – 500001,<br />India<br />+91 98765 43210</p></div></div></div></div><aside><div className="track-card"><div className="track-card-title"><h3>Payment summary</h3><span>Paid</span></div><div className="track-summary-row"><span>Subtotal</span><span>{money(subtotal || 998)}</span></div><div className="track-summary-row"><span>Delivery</span><span>{money(49)}</span></div><div className="track-summary-row"><span>Discount</span><span>₹0</span></div><div className="track-summary-row total"><span>Total paid</span><span>{money((subtotal || 998) + 49)}</span></div><div className="track-payment"><Icon name="check" /><div><strong>Payment successful</strong><span>UPI · Transaction completed</span></div></div></div><div className="track-support"><h3>Need help?</h3><p>If you have questions about delivery or your order, our support team is happy to help.</p><div className="track-support-buttons"><a href="mailto:support@poojapoint.com">Email us</a><a href="tel:+919876543210">Call us</a></div></div></aside></section>
    </main>
    <PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={cartCount} onNavChange={setNav} onWishlist={() => router.push("/wishlist")} onProfile={() => notify("Profile opened")} />
    {toast && <div className="toast show">{toast}</div>}
  </>;
}
