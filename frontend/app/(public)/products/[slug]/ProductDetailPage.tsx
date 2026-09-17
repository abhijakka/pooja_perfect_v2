"use client";

import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Icon } from "../../../../components/Icon";
import { PublicHeader } from "../../../../components/layout/PublicHeader/PublicHeader";
import { PublicFooter } from "../../../../components/layout/PublicFooter/PublicFooter";
import { useCart } from "../../../../hooks/useCart";
import { useWishlist } from "../../../../hooks/useWishlist";
import { products, type Product } from "../../storefront-data";

type ProductDetailPageProps = { product: Product };

const artNames = ["diya", "lotus", "box", "home"] as const;
const reviews = [
  ["AS", "Anjali S.", "Beautiful diya and the finish looks premium. It looks lovely in our home temple."],
  ["RK", "Rakesh K.", "Very nice packaging and the product arrived safely. Good value for the price."],
  ["PM", "Priya M.", "Bought this for gifting. The presentation is simple and elegant. Loved it."],
] as const;

function money(value: number) {
  return `₹${value.toLocaleString("en-IN")}`;
}

export default function ProductDetailPage({ product }: ProductDetailPageProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [selectedArt, setSelectedArt] = useState<(typeof artNames)[number]>("diya");
  const [quantity, setQuantity] = useState(1);
  const [pin, setPin] = useState("");
  const [deliveryResult, setDeliveryResult] = useState("");
  const { items: cart, count: cartCount, total: cartTotal, addItem, removeItem } = useCart();
  const { count: wishlistCount, contains, toggle } = useWishlist();
  const [cartOpen, setCartOpen] = useState(false);
  const [toast, setToast] = useState("");
  const [nav, setNav] = useState("products");

  useEffect(() => {
    const closeCart = (event: KeyboardEvent) => {
      if (event.key === "Escape") setCartOpen(false);
    };
    window.addEventListener("keydown", closeCart);
    return () => window.removeEventListener("keydown", closeCart);
  }, []);

  const notify = (message: string) => setToast(message);
  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(""), 1900);
    return () => window.clearTimeout(timer);
  }, [toast]);

  const suggestions = useMemo(
    () => query ? products.filter((item) => `${item.name} ${item.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : [],
    [query],
  );
  const discount = Math.round((1 - product.price / product.oldPrice) * 100);
  const related = products.filter((item) => item.id !== product.id).slice(0, 4);

  const addToCart = (item: Product, amount = 1) => {
    addItem(item, amount);
    notify(amount > 1 ? `${amount} items added to cart` : "Added to cart");
  };

  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) return notify("Type something to search");
    document.getElementById("product-details")?.scrollIntoView({ behavior: "smooth" });
  };

  const checkDelivery = () => {
    if (!/^\d{6}$/.test(pin.trim())) {
      setDeliveryResult("Please enter a valid 6-digit PIN code.");
      return;
    }
    setDeliveryResult("Delivery available. Estimated delivery: 3–6 days.");
  };

  const changeQuantity = (amount: number) => {
    setQuantity((value) => {
      const next = Math.max(1, Math.min(10, value + amount));
      if (next === 10 && amount > 0) notify("Maximum quantity is 10");
      return next;
    });
  };

  return (
    <>
      <PublicHeader query={query} suggestions={suggestions} cartCount={cartCount} wishlistCount={wishlistCount} onQueryChange={setQuery} onSearch={submitSearch} onProfile={() => notify("Profile opened")} onWishlist={() => router.push("/wishlist")} onCart={() => router.push("/cart")} />
      <div className="breadcrumb"><Link href="/">Home</Link><span>›</span><Link href={`/categories/${product.category}`}>{product.categoryLabel}</Link><span>›</span>{product.name}</div>
      <main className="product-page" id="product-details">
        <section className="product-main">
          <div className="gallery"><div className="gallery-layout"><div className="thumbnails">{artNames.map((name) => <button className={`thumbnail ${selectedArt === name ? "active" : ""}`} key={name} onClick={() => setSelectedArt(name)} aria-label={`Show ${name} view`}><Icon name={name} /></button>)}</div><div className="main-image"><button className={`gallery-wishlist ${contains(product.id) ? "active" : ""}`} onClick={() => { const saved = contains(product.id); toggle(product.id); notify(saved ? "Removed from wishlist" : "Added to wishlist"); }} aria-label="Toggle wishlist"><Icon name="heart" /></button><img className="detail-product-photo" src={product.image} alt={product.name} /><div className="zoom-label"><Icon name="search" /> Hover to view</div></div></div></div>
          <div className="product-detail-info"><div className="product-brand">PoojaPoint Premium</div><h1 className="product-title">{product.name}</h1><p className="product-subtitle">Handcrafted traditional pooja essential designed for daily pooja, festive rituals and beautiful temple décor.</p><div className="rating-row"><div className="rating-pill">{product.rating} ★</div><a href="#reviews" className="review-link">286 ratings · 74 reviews</a></div><div className="divider" /><div className="price-block"><div className="price"><span className="current-price">{money(product.price)}</span><del className="mrp">MRP {money(product.oldPrice)}</del><span className="discount">{discount}% OFF</span></div><div className="tax-note">Inclusive of all applicable taxes</div></div><div className="offer-title">Available offers</div><div className="offer-list"><div className="offer-card"><div className="offer-icon"><Icon name="tag" /></div><div><strong>10% instant discount</strong><span>Use coupon POOJA10 on orders above ₹499.</span></div></div><div className="offer-card"><div className="offer-icon"><Icon name="check" /></div><div><strong>Free delivery</strong><span>Free shipping on eligible orders above ₹999.</span></div></div></div><div className="divider" /><div className="delivery-box"><div className="delivery-head"><Icon name="truck" />Check delivery availability</div><div className="pincode-row"><input value={pin} onChange={(event) => setPin(event.target.value.replace(/\D/g, "").slice(0, 6))} inputMode="numeric" maxLength={6} placeholder="Enter PIN code" /><button className="check-btn" onClick={checkDelivery}>Check</button></div><div className={`delivery-result ${deliveryResult.startsWith("Please") ? "delivery-error" : ""}`}>{deliveryResult}</div></div><div className="buy-row"><div className="quantity"><button onClick={() => changeQuantity(-1)} aria-label="Decrease quantity">−</button><span>{quantity}</span><button onClick={() => changeQuantity(1)} aria-label="Increase quantity">+</button></div><button className="cart-button" onClick={() => addToCart(product, quantity)}>Add to Cart</button><button className="buy-button" onClick={() => { addToCart(product, quantity); setCartOpen(true); }}>Buy Now</button></div><div className="product-trust"><div className="product-trust-card"><Icon name="truck" /><div><strong>Fast delivery</strong><span>Carefully packed and shipped.</span></div></div><div className="product-trust-card"><Icon name="shield" /><div><strong>Secure payment</strong><span>Safe checkout experience.</span></div></div><div className="product-trust-card"><Icon name="return" /><div><strong>Easy returns</strong><span>Simple customer support.</span></div></div></div></div>
        </section>
        <section className="details-section"><div className="details-grid"><div><h2 className="details-title">Product details</h2><p className="details-copy">Bring a warm and traditional touch to your sacred space with our {product.name}. Its timeless finish complements both traditional home temples and modern interiors.<br /><br />Designed for daily prayer, festivals, special occasions and gifting, this product is easy to use and makes a beautiful addition to your pooja collection.</p><div className="highlights"><div className="highlight"><strong>Premium finish</strong><span>Elegant traditional appearance.</span></div><div className="highlight"><strong>Everyday use</strong><span>Suitable for daily pooja rituals.</span></div><div className="highlight"><strong>Festive ready</strong><span>Perfect for festive décor.</span></div><div className="highlight"><strong>Gift worthy</strong><span>Beautiful devotional gifting choice.</span></div></div></div><div><h2 className="details-title">Specifications</h2><div className="spec-box"><div className="spec-row"><div>Material</div><div>Brass</div></div><div className="spec-row"><div>Product type</div><div>{product.categoryLabel}</div></div><div className="spec-row"><div>Colour</div><div>Antique Gold</div></div><div className="spec-row"><div>Usage</div><div>Pooja / Decor</div></div><div className="spec-row"><div>Pack</div><div>1 piece</div></div><div className="spec-row"><div>Care</div><div>Wipe with dry cloth</div></div></div></div></div></section>
        <section className="reviews-section" id="reviews"><h2 className="details-title">Customer reviews</h2><div className="reviews-summary"><div className="average-rating"><strong>{product.rating}</strong><div className="stars">★★★★★</div><span>74 verified reviews</span></div><div className="rating-bars">{[["5★", "91%", "91%"], ["4★", "7%", "7%"], ["3★", "2%", "2%"], ["2★", "0%", "0%"], ["1★", "0%", "0%"]].map(([label, width, value]) => <div className="rating-bar" key={label}><span>{label}</span><div className="bar"><div className="bar-fill" style={{ width }} /></div><span>{value}</span></div>)}</div></div><div className="review-list">{reviews.map(([initials, name, text]) => <article className="review-card" key={name}><div className="reviewer"><div className="avatar">{initials}</div><div><strong>{name}</strong><span className="verified">✓ Verified purchase</span></div></div><div className="review-stars">★★★★★</div><p>{text}</p></article>)}</div></section>
        <section className="related"><h2 className="details-title">You may also like</h2><div className="related-product-grid">{related.map((item) => <article className="product-card" key={item.id}><Link href={`/products/${item.slug}`}><div className="product-image"><img className="product-photo" src={item.image} alt={item.name} /></div></Link><div className="product-info"><div className="product-category">{item.categoryLabel}</div><h3 className="product-name">{item.name}</h3><div className="product-price"><span className="current">{money(item.price)}</span><del className="mrp">{money(item.oldPrice)}</del></div><button className="add-cart" onClick={() => addToCart(item)}>Add to Cart</button></div></article>)}</div></section>
      </main>
      <PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={cartCount} onNavChange={setNav} onWishlist={() => router.push("/wishlist")} onProfile={() => notify("Profile opened")} />
      {cartOpen && <><button className="cart-overlay show" onClick={() => setCartOpen(false)} aria-label="Close cart" /><aside className="cart open"><div className="cart-head"><h2>Your cart</h2><button className="close-cart" onClick={() => setCartOpen(false)} aria-label="Close cart">×</button></div><div className="cart-items">{cart.length ? cart.map((item) => <div className="cart-item" key={item.id}><button className="remove" onClick={() => removeItem(item.id)}>×</button><strong>{item.name}</strong><div className="cart-item-price">{money(item.price)} × {item.quantity}</div></div>) : <div className="empty">Your cart is empty.</div>}</div><div className="cart-total"><div className="total-row"><span>Total</span><strong>{money(cartTotal)}</strong></div><button className="checkout" onClick={() => notify(cart.length ? "Ready for checkout integration" : "Your cart is empty")}>Continue to checkout →</button></div></aside></>}
      {toast && <div className="toast show">{toast}</div>}
    </>
  );
}
