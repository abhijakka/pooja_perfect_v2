"use client";

import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import { useFormik } from "formik";
import * as yup from "yup";
import { email, name, phone } from "../../../lib/validation";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Icon } from "../../../components/Icon";
import { PublicHeader } from "../../../components/layout/PublicHeader/PublicHeader";
import { PublicFooter } from "../../../components/layout/PublicFooter/PublicFooter";
import { useCart } from "../../../hooks/useCart";
import { useWishlist } from "../../../hooks/useWishlist";
import { products } from "../storefront-data";
import { checkoutApi } from "../../../services/api/checkout.api";
import { couponApi } from "../../../services/api/coupon.api";

type PaymentMethod = "upi" | "card" | "netbanking" | "cod";

const savedAddress = {
  name: "Ananya Sharma",
  phone: "+91 98765 43210",
  line: "12, Lotus Residency, Andheri West",
  city: "Mumbai, Maharashtra 400058",
};

export default function CheckoutPage() {
  const router = useRouter();
  const { items, count, total, clearCart } = useCart();
  const { count: wishlistCount } = useWishlist();
  const [query, setQuery] = useState("");
  const [nav, setNav] = useState("shop");
  const [addressMode, setAddressMode] = useState<"home" | "new">("new");
  const [deliveryKey, setDeliveryKey] = useState<"standard" | "express" | "free">("standard");
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("upi");
  const [couponInput, setCouponInput] = useState("");
  const [couponDiscount, setCouponDiscount] = useState(0);
  const [couponMessage, setCouponMessage] = useState("");
  const [couponLoading, setCouponLoading] = useState(false);
  const [orderNote, setOrderNote] = useState("");
  const [terms, setTerms] = useState(false);
  const [toast, setToast] = useState("");

  const suggestions = useMemo(
    () => (query ? products.filter((item) => `${item.name} ${item.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : []),
    [query],
  );

  const money = (value: number) => `₹${value.toLocaleString("en-IN")}`;
  const deliveryOptions = [
    { key: "standard" as const, label: "Standard Delivery", eta: "4-6 business days", cost: total > 0 && total < 1000 ? 49 : 0, icon: "truck" },
    { key: "express" as const, label: "Express Delivery", eta: "1-2 business days", cost: 99, icon: "arrow-right" },
    { key: "free" as const, label: "Pickup from Store", eta: "Ready in 2 hours", cost: 0, icon: "home" },
  ];
  const selectedDelivery = deliveryOptions.find((option) => option.key === deliveryKey) ?? deliveryOptions[0];
  const deliveryCost = selectedDelivery.cost;
  const grandTotal = Math.max(0, total - couponDiscount + deliveryCost);

  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2200);
  };
  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) notify("Type something to search");
  };
  const applyCoupon = async () => {
    const code = couponInput.trim().toUpperCase();
    if (!code) {
      setCouponDiscount(0);
      setCouponMessage("Enter a coupon code.");
      return;
    }
    setCouponLoading(true);
    try {
      const { applyCoupon: result } = await couponApi.apply(code, total);
      if (result && Number(result.discount) > 0) {
        const discount = Math.min(Number(result.discount), total);
        setCouponDiscount(discount);
        setCouponMessage(`Coupon applied — ${result.code} (${result.couponType === "percentage" ? `${Number(result.value)}% off up to ₹${Number(result.maximumDiscount ?? discount)}` : `₹${Number(result.value)} off`})`);
        notify("Coupon applied successfully");
      } else {
        setCouponDiscount(0);
        setCouponMessage("Invalid coupon code.");
      }
    } catch {
      setCouponDiscount(0);
      setCouponMessage("Invalid coupon code.");
    } finally {
      setCouponLoading(false);
    }
  };
  const readAddress = (values: typeof formik.initialValues) => {
    if (addressMode === "home") return savedAddress;
    const { firstName, lastName, phone, address, city, state, pin } = values;
    return { name: [firstName, lastName].filter(Boolean).join(" ") || "Customer", phone: phone || "—", line: address || "—", city: [city, state, pin].filter(Boolean).join(", ") || "—" };
  };
  const formik = useFormik({
    initialValues: { firstName: "", lastName: "", phone: "", email: "", address: "", city: "", state: "", pin: "", type: "Home" },
    validationSchema: addressMode === "new" ? yup.object({
      firstName: name.required("Enter your first name"),
      lastName: name.required("Enter your last name"),
      phone: phone.required("Enter your phone number"),
      email: email.required("Enter your email address"),
      address: yup.string().required("Enter your address"),
      city: yup.string().required("Enter your city"),
      state: yup.string().required("Enter your state"),
      pin: yup.string().matches(/^[0-9]{6}$/, "Enter a valid 6-digit pin code").required("Enter your pin code"),
      type: yup.string(),
    }) : undefined,
    onSubmit: async (values) => {
      if (!items.length) return notify("Your cart is empty");
      if (!terms) return notify("Please accept the terms and conditions");
      const address = readAddress(values);
      try {
        const { checkout } = await checkoutApi.placeOrder({
          recipientName: address.name,
          phone: address.phone,
          addressLine1: address.line,
          city: values.city,
          state: values.state,
          postalCode: values.pin,
          country: "India",
          paymentMethod,
          couponCode: couponInput.trim().toUpperCase() || undefined,
          notes: orderNote || undefined,
        });
        const order = checkout.order;
        window.sessionStorage.setItem("pp_last_order", JSON.stringify({
          orderId: order.orderNumber,
          placedAt: order.createdAt,
          items: order.items.map((item) => ({ id: item.id, name: item.productName, price: Number(item.unitPrice), quantity: item.quantity, image: "" })),
          subtotal: Number(order.subtotal),
          delivery: Number(order.shippingCharge),
          deliveryOption: selectedDelivery.label,
          couponDiscount: Number(order.discount),
          grandTotal: Number(order.total),
          paymentMethod,
          orderNote: order.notes || undefined,
          address,
        }));
        clearCart();
        router.push("/order/confirmation");
      } catch (error) {
        notify(error instanceof Error ? error.message : "Order could not be placed");
      }
    },
  });
  const addressField = (name: "firstName" | "lastName" | "phone" | "email" | "address" | "city" | "state" | "pin", label: string, placeholder: string, full = false, extra: Record<string, unknown> = {}) => (
    <div className={`form-group${full ? " full" : ""}`}><label>{label} <span>*</span></label><input {...formik.getFieldProps(name)} placeholder={placeholder} {...extra} />{formik.touched[name] && formik.errors[name] && <small className="form-error">{formik.errors[name]}</small>}</div>
  );

  const paymentMethods: { key: PaymentMethod; label: string; hint: string; icon: string }[] = [
    { key: "upi", label: "UPI", hint: "Pay via GPay, PhonePe, Paytm", icon: "wallet" },
    { key: "card", label: "Credit / Debit Card", hint: "Visa, Mastercard, RuPay", icon: "card" },
    { key: "netbanking", label: "Net Banking", hint: "All major banks supported", icon: "lock" },
    { key: "cod", label: "Cash on Delivery", hint: "Pay when your order arrives", icon: "truck" },
  ];

  return <>
    <PublicHeader query={query} suggestions={suggestions} cartCount={count} wishlistCount={wishlistCount} onQueryChange={setQuery} onSearch={submitSearch} onProfile={() => notify("Profile opened")} onWishlist={() => router.push("/wishlist")} onCart={() => router.push("/cart")} />
    <main className="checkout-page checkout-exact-page">
      <div className="breadcrumb"><Link href="/">Home</Link><span>›</span><Link href="/cart">Cart</Link><span>›</span>Checkout</div>
      <div className="checkout-heading"><h1>Checkout</h1><p>Complete your order securely. Review your details below.</p></div>
      <form className="checkout-layout" onSubmit={formik.handleSubmit} noValidate>
        <div className="checkout-left">
          <section className="checkout-card">
            <div className="card-heading"><h2><span className="number">1</span> Delivery Address</h2><small>Where should we deliver?</small></div>
            <div className="address-options">
              <button type="button" className={`address-option ${addressMode === "home" ? "active" : ""}`} onClick={() => setAddressMode("home")}>
                <span className="address-top"><strong>Saved Address</strong><span className="address-type">HOME</span></span>
                <p>{savedAddress.name} · {savedAddress.phone}<br />{savedAddress.line}, {savedAddress.city}</p>
              </button>
              <button type="button" className={`address-option ${addressMode === "new" ? "active" : ""}`} onClick={() => setAddressMode("new")}>
                <span className="address-top"><strong>Add New Address</strong><span className="address-type">NEW</span></span>
                <p>Enter a fresh delivery address for this order.</p>
              </button>
            </div>
            {addressMode === "new" && <div className="form-grid">
              {addressField("firstName", "First name", "Ananya")}
              {addressField("lastName", "Last name", "Sharma")}
              {addressField("phone", "Phone", "+91 98765 43210", false, { type: "tel" })}
              {addressField("email", "Email", "you@example.com", false, { type: "email" })}
              {addressField("address", "Address line", "Flat / house no, street, area", true)}
              {addressField("city", "City", "Mumbai")}
              {addressField("state", "State", "Maharashtra")}
              {addressField("pin", "Pin code", "400058", false, { inputMode: "numeric", pattern: "[0-9]{6}" })}
              <div className="form-group"><label>Address type</label><select {...formik.getFieldProps("type")}><option>Home</option><option>Office</option><option>Other</option></select></div>
            </div>}
          </section>

          <section className="checkout-card">
            <div className="card-heading"><h2><span className="number">2</span> Delivery Method</h2><small>Choose your speed</small></div>
            <div className="delivery-options">
              {deliveryOptions.map((option) => <button type="button" key={option.key} className={`delivery-option ${deliveryKey === option.key ? "active" : ""}`} onClick={() => setDeliveryKey(option.key)}>
                <span className="delivery-icon"><Icon name={option.icon} /></span>
                <span className="delivery-info"><strong>{option.label}</strong><span>{option.eta}</span></span>
                <span className="delivery-price">{option.cost ? money(option.cost) : "FREE"}</span>
              </button>)}
            </div>
          </section>

          <section className="checkout-card">
            <div className="card-heading"><h2><span className="number">3</span> Payment Method</h2><small>100% secure</small></div>
            <div className="payment-options">
              {paymentMethods.map((method) => <button type="button" key={method.key} className={`payment-option ${paymentMethod === method.key ? "active" : ""}`} onClick={() => setPaymentMethod(method.key)}>
                <span className="payment-icon"><Icon name={method.icon} /></span>
                <span className="payment-info"><strong>{method.label}</strong><span>{method.hint}</span></span>
                {paymentMethod === method.key && <span className="payment-check"><Icon name="check" /></span>}
              </button>)}
            </div>
          </section>

          <section className="checkout-card">
            <div className="card-heading"><h2><span className="number">4</span> Order Notes</h2><small>Optional</small></div>
            <div className="form-group full"><label>Delivery instructions</label><textarea rows={3} value={orderNote} onChange={(event) => setOrderNote(event.target.value)} placeholder="Ring the bell, leave at the door, gift wrap, etc." /></div>
          </section>
        </div>

        <aside className="co-summary">
          <h2>Order Summary</h2>
          <div className="order-items">
            {items.length ? items.map((item) => <div className="order-item" key={item.id}>
              <span className="order-image">{item.image ? <img src={item.image} alt={item.name} /> : <Icon name="box" />}</span>
              <span className="order-details"><strong>{item.name}</strong><span>Qty {item.quantity}</span></span>
              <span className="order-price">{money(item.price * item.quantity)}</span>
            </div>) : <p className="summary-empty">Your cart is empty. Add products before placing an order.</p>}
          </div>
          <div className="co-coupon">
            <input value={couponInput} onChange={(event) => setCouponInput(event.target.value)} placeholder="Coupon code" />
            <button type="button" onClick={applyCoupon} disabled={couponLoading}>{couponLoading ? "..." : "Apply"}</button>
          </div>
          {couponMessage && <div className={`co-coupon-message ${couponMessage.includes("Invalid") || couponMessage.includes("Enter") ? "error" : ""}`}>{couponMessage}</div>}
          <div className="price-lines">
            <div className="price-line"><span>Subtotal</span><strong>{money(total)}</strong></div>
            {couponDiscount > 0 && <div className="price-line discount"><span>Coupon discount</span><strong>-{money(couponDiscount)}</strong></div>}
            <div className="price-line"><span>Delivery</span><strong>{deliveryCost ? money(deliveryCost) : "FREE"}</strong></div>
            <div className="price-line total"><span>Total</span><strong>{money(grandTotal)}</strong></div>
          </div>
          <label className="terms"><input type="checkbox" checked={terms} onChange={(event) => setTerms(event.target.checked)} /> I agree to the <Link href="/">Terms of Service</Link> and <Link href="/">Privacy Policy</Link>.</label>
          <button type="submit" className="place-order" disabled={!items.length}>Place Order · {money(grandTotal)}</button>
          <div className="summary-trust">
            <div className="summary-trust-item"><Icon name="shield" /><span>Secure</span></div>
            <div className="summary-trust-item"><Icon name="truck" /><span>Fast delivery</span></div>
            <div className="summary-trust-item"><Icon name="refresh" /><span>Easy returns</span></div>
          </div>
        </aside>
      </form>
    </main>
    <PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={count} onNavChange={setNav} onWishlist={() => router.push("/wishlist")} onProfile={() => notify("Profile opened")} />
    {toast && <div className="toast show">{toast}</div>}
  </>;
}
