"use client";

import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import { Icon } from "../../../components/Icon";
import { PublicHeader } from "../../../components/layout/PublicHeader/PublicHeader";
import { PublicFooter } from "../../../components/layout/PublicFooter/PublicFooter";
import { RemoveConfirmationModal } from "../../../components/cart/RemoveConfirmationModal";
import { useCart } from "../../../hooks/useCart";
import { useWishlist } from "../../../hooks/useWishlist";
import { RecommendationsCarousel, type StoreProduct } from "../../../components/product/ProductCard";
import { products } from "../storefront-data";

export default function CartPage() {
  const { items, count, total, updateQuantity, removeItem, clearCart, addItem } = useCart();
  const { items: wishlist, count: wishlistCount, toggle } = useWishlist();
  const [query, setQuery] = useState("");
  const [coupon, setCoupon] = useState("");
  const [couponDiscount, setCouponDiscount] = useState(0);
  const [couponMessage, setCouponMessage] = useState("");
  const [toast, setToast] = useState("");
  const [nav, setNav] = useState("shop");
  const [itemToRemove, setItemToRemove] = useState<string | null>(null);
  const [clearCartOpen, setClearCartOpen] = useState(false);
  const suggestions = useMemo(() => query ? products.filter((item) => `${item.name} ${item.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : [], [query]);
  const money = (value: number) => `₹${value.toLocaleString("en-IN")}`;
  const originalTotal = items.reduce((sum, item) => sum + item.oldPrice * item.quantity, 0);
  const productDiscount = originalTotal - total;
  const deliveryFee = total > 0 && total < 1000 ? 49 : 0;
  const grandTotal = total - couponDiscount + deliveryFee;
  const progress = Math.min(100, (total / 1000) * 100);
  const remaining = Math.max(0, 1000 - total);

  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2200);
  };
  const recommended = products.filter((item) => !items.some((cartItem) => cartItem.id === item.id)).slice(0, 8);
  const addToCart = (product: StoreProduct) => {
    addItem(product);
    notify("Added to cart");
  };
  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) notify("Type something to search");
  };
  const applyCoupon = () => {
    const code = coupon.trim().toUpperCase();
    if (!code) {
      setCouponDiscount(0);
      setCouponMessage("Enter a coupon code.");
    } else if (code === "POOJA10") {
      setCouponDiscount(Math.min(100, Math.floor(total * 0.1)));
      setCouponMessage("✓ Coupon applied — 10% OFF up to ₹100");
      notify("Coupon applied successfully");
    } else {
      setCouponDiscount(0);
      setCouponMessage("Invalid coupon code.");
    }
  };
  const confirmRemove = (id: string) => {
    setItemToRemove(id);
  };
  const confirmRemoveItem = () => {
    if (!itemToRemove) return;
    removeItem(itemToRemove);
    setItemToRemove(null);
    notify("Item removed from cart");
  };
  const confirmClear = () => {
    if (!items.length) return notify("Your cart is already empty");
    setClearCartOpen(true);
  };
  const confirmClearCart = () => {
    clearCart();
    setClearCartOpen(false);
    notify("Cart cleared");
  };

  return <>
    <PublicHeader query={query} suggestions={suggestions} cartCount={count} wishlistCount={wishlistCount} onQueryChange={setQuery} onSearch={submitSearch} onProfile={() => notify("Profile opened")} onWishlist={() => window.location.assign("/wishlist")} onCart={() => window.scrollTo({ top: 0, behavior: "smooth" })} />
    <main className="cart-page cart-exact-page">
      <div className="breadcrumb"><Link href="/">Home</Link><span>›</span>Shopping Cart</div>
      <div className="cart-header"><div><h1 className="cart-title">Your Cart</h1><p className="cart-subtitle">{count ? `${count} ${count === 1 ? "item" : "items"} ready for checkout` : "Your cart is empty"}</p></div><Link href="/products" className="continue-shopping">Continue Shopping <Icon name="arrow-right" /></Link></div>
      <div className="delivery-progress"><div className="delivery-progress-top"><strong>{total >= 1000 ? "You unlocked FREE delivery!" : total ? `You are ${money(remaining)} away from FREE delivery` : "Add products to unlock FREE delivery"}</strong><span>₹1,000 minimum</span></div><div className="progress-track"><div className="progress-fill" style={{ width: `${progress}%` }} /></div></div>
      <div className="cart-grid">
        <section className="cart-card"><div className="cart-card-header"><h2>Shopping Cart (<span>{count}</span>)</h2><button className="select-all" onClick={confirmClear}>Clear Cart</button></div><div className={`cart-items ${!items.length ? "cart-items-empty" : ""}`}>{items.map((item) => {
                const payGo = item.categoryLabel === "Pay As You Go";
                return (
                  <article className={`cart-item ${payGo ? "paygo-item" : ""}`} key={item.id}>
                    <Link href={payGo ? "#" : `/products/${item.slug}`} className="product-image">
                      {payGo ? (
                        <span className="discount-badge paygo-badge">PAYGO</span>
                      ) : (
                        <span className="discount-badge">{Math.round((1 - item.price / item.oldPrice) * 100)}% OFF</span>
                      )}
                      <img src={item.image} alt={item.name} />
                    </Link>
                    <div className="product-info">
                      <div className="product-category">{payGo ? "Pay As You Go" : item.categoryLabel}</div>
                      <Link href={payGo ? "#" : `/products/${item.slug}`}><h3 className="product-name">{item.name}</h3></Link>
                      {payGo ? (
                        <p className="product-description">Custom pack · {item.category} · {money(item.price)} per delivery</p>
                      ) : (
                        <p className="product-description">Premium pooja essential suitable for daily worship and festive occasions.</p>
                      )}
                      <div className="product-meta">
                        {payGo ? (
                          <>
                            <span className="meta-pill">Pay As You Go</span>
                            <span className="meta-pill">{item.category}</span>
                            <span className="meta-pill">Custom pack</span>
                          </>
                        ) : (
                          <>
                            <span className="meta-pill">Premium</span>
                            <span className="meta-pill">In Stock</span>
                            <span className="meta-pill">Secure pack</span>
                          </>
                        )}
                      </div>
                      <div className="price-row">
                        <span className="current-price">{money(item.price)}</span>
                        {!payGo && <span className="old-price">{money(item.oldPrice)}</span>}
                        {!payGo && <span className="save-price">Save {money(item.oldPrice - item.price)}</span>}
                      </div>
                      <div className="item-actions">
                        <button className="item-action" onClick={() => { const saved = wishlist.includes(item.id); toggle(item.id); notify(saved ? "Removed from wishlist" : "Added to wishlist"); }}><Icon name="heart" /> Wishlist</button>
                        <button className="item-action delete" onClick={() => confirmRemove(item.id)}><Icon name="trash" /> Remove</button>
                      </div>
                    </div>
                    <div className="item-right">
                      <div className="quantity">
                        <button onClick={() => updateQuantity(item.id, item.quantity - 1)} aria-label="Decrease quantity"><Icon name="minus" /></button>
                        <span>{item.quantity}</span>
                        <button onClick={() => updateQuantity(item.id, Math.min(10, item.quantity + 1))} aria-label="Increase quantity"><Icon name="plus" /></button>
                      </div>
                      <div className="item-total">{money(item.price * item.quantity)}</div>
                    </div>
                  </article>
                );
              })}</div>{!items.length && <div className="empty-cart show"><div className="empty-icon"><Icon name="cart" /></div><h2>Your cart is empty</h2><p>Looks like you haven&apos;t added anything to your cart yet. Explore our beautiful collection of pooja essentials.</p><Link href="/products" className="shop-button">Start Shopping</Link></div>}</section>
        <aside className="summary"><h2>Order Summary</h2><div className="coupon"><div className="coupon-title"><Icon name="tag" /> Have a coupon?</div><div className="coupon-row"><input value={coupon} onChange={(event) => setCoupon(event.target.value)} placeholder="Enter coupon code" /><button className="coupon-button" onClick={applyCoupon}>Apply</button></div><div className={`coupon-message ${couponMessage.includes("Invalid") || couponMessage.includes("Enter") ? "coupon-error" : ""}`}>{couponMessage}</div></div><div className="summary-rows"><div className="summary-row"><span>Subtotal</span><strong>{money(total)}</strong></div><div className="summary-row discount"><span>Product discount</span><strong>-{money(productDiscount)}</strong></div><div className="summary-row discount"><span>Coupon discount</span><strong>-{money(couponDiscount)}</strong></div><div className="summary-row delivery"><span>Delivery</span><strong>{deliveryFee ? money(deliveryFee) : "FREE"}</strong></div></div><div className="total-row"><span>Total</span><strong>{money(grandTotal)}</strong></div><Link href={items.length ? "/checkout" : "/products"} className="checkout-button" onClick={(event) => { if (!items.length) { event.preventDefault(); notify("Your cart is empty"); } }}>Proceed to Checkout <Icon name="arrow-right" /></Link><div className="secure-note"><Icon name="lock" /> Secure checkout · Your information is protected</div><div className="payment-methods"><span className="payment">UPI</span><span className="payment">VISA</span><span className="payment">RuPay</span><span className="payment">NetBanking</span><span className="payment">COD</span></div><div className="benefits"><div className="benefit"><div className="benefit-icon"><Icon name="truck" /></div><span>Fast delivery</span></div><div className="benefit"><div className="benefit-icon"><Icon name="refresh" /></div><span>Easy returns</span></div><div className="benefit"><div className="benefit-icon"><Icon name="shield" /></div><span>Secure payment</span></div></div></aside>
      </div>
      <RecommendationsCarousel products={recommended} wishlist={wishlist} onWishlistToggle={toggle} onAddToCart={addToCart} />
    </main>
    <PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={count} onNavChange={setNav} onWishlist={() => window.location.assign("/wishlist")} onProfile={() => notify("Profile opened")} />
    {toast && <div className="toast show">{toast}</div>}
    <RemoveConfirmationModal open={Boolean(itemToRemove)} onCancel={() => setItemToRemove(null)} onConfirm={confirmRemoveItem} />
    <RemoveConfirmationModal open={clearCartOpen} title="Clear Cart?" message="Are you sure you want to remove all items from your cart?" confirmLabel="Clear Cart" onCancel={() => setClearCartOpen(false)} onConfirm={confirmClearCart} />
  </>;
}
