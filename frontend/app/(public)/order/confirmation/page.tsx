"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Icon } from "../../../../components/Icon";
import { PublicHeader } from "../../../../components/layout/PublicHeader/PublicHeader";
import { PublicFooter } from "../../../../components/layout/PublicFooter/PublicFooter";
import { useCart } from "../../../../hooks/useCart";
import { useWishlist } from "../../../../hooks/useWishlist";
import { products } from "../../storefront-data";

type PaymentMethod = "upi" | "card" | "netbanking" | "cod";

type OrderItem = { id: string; name: string; price: number; quantity: number; image: string };

type OrderSnapshot = {
  orderId: string;
  placedAt: string;
  items: OrderItem[];
  subtotal: number;
  delivery: number;
  deliveryOption: string;
  couponDiscount: number;
  grandTotal: number;
  paymentMethod: PaymentMethod;
  orderNote?: string;
  address: { name: string; phone: string; line: string; city: string };
};

const paymentLabels: Record<PaymentMethod, string> = {
  upi: "UPI Payment",
  card: "Credit / Debit Card",
  netbanking: "Net Banking",
  cod: "Cash on Delivery",
};

function deliveryWindow(placedAt: string, deliveryOption: string): string {
  const days = /express/i.test(deliveryOption) ? 2 : /pickup/i.test(deliveryOption) ? 0 : 5;
  const start = new Date(placedAt); start.setDate(start.getDate() + Math.max(0, days - 2));
  const end = new Date(placedAt); end.setDate(end.getDate() + days);
  const fmt = (d: Date) => d.toLocaleDateString("en-IN", { month: "short", day: "numeric" });
  return `${fmt(start)} – ${fmt(end)}`;
}

const timelineSteps = [
  { icon: "check", title: "Order confirmed", text: "Your order has been received", done: true },
  { icon: "box", title: "Preparing your order", text: "Our team is carefully packing your items", done: false },
  { icon: "truck", title: "Shipped", text: "You'll receive tracking details", done: false },
  { icon: "location", title: "Delivered", text: "Your pooja essentials arrive safely", done: false },
];

const productIcons = ["diya", "lotus", "box", "sparkle"];

export default function ConfirmationPage() {
  const router = useRouter();
  const { count } = useCart();
  const { count: wishlistCount } = useWishlist();
  const [order, setOrder] = useState<OrderSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [nav, setNav] = useState("shop");
  const [toast, setToast] = useState("");

  const suggestions = useMemo(
    () => (query ? products.filter((item) => `${item.name} ${item.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : []),
    [query],
  );

  const processedRef = useRef(false);
  useEffect(() => {
    if (processedRef.current) return;
    processedRef.current = true;
    const raw = typeof window !== "undefined" ? window.sessionStorage.getItem("pp_last_order") : null;
    if (!raw) {
      router.replace("/products");
      return;
    }
    try {
      setOrder(JSON.parse(raw) as OrderSnapshot);
    } catch {
      router.replace("/products");
      return;
    }
    window.sessionStorage.removeItem("pp_last_order");
    setLoading(false);
  }, [router]);

  const money = (value: number) => `₹${value.toLocaleString("en-IN")}`;
  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2200);
  };
  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) notify("Type something to search");
  };

  const deliveryWindowText = order ? deliveryWindow(order.placedAt, order.deliveryOption) : "";
  const totalItems = order ? order.items.reduce((sum, item) => sum + item.quantity, 0) : 0;

  return <>
    <PublicHeader query={query} suggestions={suggestions} cartCount={count} wishlistCount={wishlistCount} onQueryChange={setQuery} onSearch={submitSearch} onProfile={() => notify("Profile opened")} onWishlist={() => router.push("/wishlist")} onCart={() => router.push("/cart")} />
    <main className="confirmation-exact-page">
      {loading || !order ? <div className="confirmation-loading"><span className="confirmation-spinner" /> Preparing your order…</div> : <>
        <div className="breadcrumb"><Link href="/">Home</Link><span>›</span><Link href="/cart">Cart</Link><span>›</span>Order Confirmation</div>

        <section className="cn-success">
          <div className="cn-success-icon"><Icon name="check" /></div>
          <small>Order successfully placed</small>
          <h1>Thank you for your order ✨</h1>
          <p>Your order has been confirmed. We are carefully preparing your beautiful pooja essentials and will keep you updated at every step.</p>
          <div className="cn-order-id">Order ID: <span>{order.orderId}</span></div>
          <div className="cn-hero-buttons">
            <button className="cn-btn cn-btn-primary" onClick={() => { notify("Opening order tracking…"); router.push("/order/track"); }}><Icon name="truck" /> Track Order</button>
            <button className="cn-btn cn-btn-secondary" onClick={() => router.push("/products")}>Continue Shopping</button>
          </div>
        </section>

        <div className="cn-grid">
          <div>
            <section className="cn-card">
              <div className="cn-card-title"><h2>Your items</h2><span>{totalItems} {totalItems === 1 ? "item" : "items"}</span></div>

              {order.items.map((item, index) => <div className="cn-product" key={item.id}>
                <span className="cn-product-img">{item.image ? <img src={item.image} alt={item.name} /> : <Icon name={productIcons[index % productIcons.length]} />}</span>
                <span className="cn-product-info"><strong>{item.name}</strong><span>Quantity: {item.quantity}</span></span>
                <span className="cn-product-price">{money(item.price * item.quantity)}</span>
              </div>)}

              <div className="cn-status">
                <div className="cn-status-top">
                  <span className="cn-status-label"><Icon name="truck" /> Estimated delivery</span>
                  <span className="cn-status-date">{deliveryWindowText}</span>
                </div>
                <p>We'll send you tracking updates once your order leaves our fulfilment centre.</p>
              </div>

              <div className="cn-timeline">
                {timelineSteps.map((step) => <div className={`cn-tl-item ${step.done ? "completed" : ""}`} key={step.title}>
                  <span className="cn-tl-dot"><Icon name={step.icon} /></span>
                  <div className="cn-tl-content"><strong>{step.title}</strong><span>{step.text}</span></div>
                </div>)}
              </div>

              {order.orderNote && <div className="cn-note">{order.orderNote}</div>}
            </section>

            <section className="cn-card">
              <div className="cn-card-title"><h2>Delivery address</h2><span>Shipping</span></div>
              <div className="cn-address">
                <span className="cn-address-icon"><Icon name="location" /></span>
                <div>
                  <strong>{order.address.name}</strong>
                  <p>{order.address.line},<br />{order.address.city}<br />{order.address.phone}</p>
                </div>
              </div>
            </section>
          </div>

          <aside>
            <section className="cn-card">
              <div className="cn-card-title"><h2>Order summary</h2><span>{order.paymentMethod === "cod" ? "Due" : "Paid"}</span></div>

              <div className="cn-summary-row"><span>Subtotal</span><span>{money(order.subtotal)}</span></div>
              <div className="cn-summary-row"><span>Delivery</span><span>{order.delivery ? money(order.delivery) : "FREE"}</span></div>
              {order.couponDiscount > 0 && <div className="cn-summary-row discount"><span>Discount</span><span>-{money(order.couponDiscount)}</span></div>}
              <div className="cn-summary-row"><span>Tax</span><span>Included</span></div>
              <div className="cn-summary-row total"><span>Total {order.paymentMethod === "cod" ? "due" : "paid"}</span><span>{money(order.grandTotal)}</span></div>

              <div className="cn-payment-status">
                <Icon name={order.paymentMethod === "cod" ? "truck" : "check"} />
                <div>
                  <strong>{order.paymentMethod === "cod" ? "Pay on delivery" : "Payment successful"}</strong>
                  <span>{paymentLabels[order.paymentMethod]}{order.paymentMethod === "cod" ? "" : " · Transaction completed"}</span>
                </div>
              </div>
            </section>

            <section className="cn-help">
              <h3>Need help?</h3>
              <p>Our support team is happy to help with your order, delivery or product questions.</p>
              <button className="cn-help-btn" onClick={() => notify("Opening support…")}>Contact Support</button>
            </section>
          </aside>
        </div>
      </>}
    </main>
    <PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={count} onNavChange={setNav} onWishlist={() => router.push("/wishlist")} onProfile={() => notify("Profile opened")} />
    {toast && <div className="toast show">{toast}</div>}
  </>;
}
