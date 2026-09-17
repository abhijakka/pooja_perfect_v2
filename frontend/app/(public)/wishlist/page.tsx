"use client";

import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Icon } from "../../../components/Icon";
import { PublicFooter } from "../../../components/layout/PublicFooter/PublicFooter";
import { PublicHeader } from "../../../components/layout/PublicHeader/PublicHeader";
import { RemoveConfirmationModal } from "../../../components/cart/RemoveConfirmationModal";
import { useCart } from "../../../hooks/useCart";
import { useWishlist } from "../../../hooks/useWishlist";
import { products } from "../storefront-data";

function money(value: number) {
  return `₹${value.toLocaleString("en-IN")}`;
}

export default function WishlistPage() {
  const router = useRouter();
  const { items, count, add, remove } = useWishlist();
  const { count: cartCount, addItem } = useCart();
  const [query, setQuery] = useState("");
  const [toast, setToast] = useState("");
  const [nav, setNav] = useState("wishlist");
  const [itemToRemove, setItemToRemove] = useState<string | null>(null);
  const [clearWishlistOpen, setClearWishlistOpen] = useState(false);
  const suggestions = useMemo(() => query ? products.filter((item) => `${item.name} ${item.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : [], [query]);
  const savedProducts = products.filter((product) => items.includes(product.id));

  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2200);
  };
  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) notify("Type something to search");
  };
  const addToCart = (product: (typeof products)[number]) => {
    addItem(product);
    notify(`${product.name} added to cart`);
  };
  const confirmRemoveItem = () => {
    if (!itemToRemove) return;
    remove(itemToRemove);
    setItemToRemove(null);
    notify("Removed from wishlist");
  };
  const confirmClearWishlist = () => {
    items.forEach(remove);
    setClearWishlistOpen(false);
    notify("Wishlist cleared");
  };

  return <>
    <PublicHeader query={query} suggestions={suggestions} cartCount={cartCount} wishlistCount={count} onQueryChange={setQuery} onSearch={submitSearch} onProfile={() => notify("Profile opened")} onWishlist={() => setNav("wishlist")} onCart={() => router.push("/cart")} />
    <main className="wishlist-page wishlist-exact-page">
      <div className="breadcrumb"><Link href="/">Home</Link><span>›</span>Wishlist</div>
      <div className="wishlist-header"><div><h1 className="wishlist-title">Your Wishlist</h1><p className="wishlist-subtitle">{count ? `${count} ${count === 1 ? "item" : "items"} saved for later` : "Keep your favourite ritual essentials close"}</p></div><Link href="/products" className="continue-shopping">Continue Shopping <Icon name="arrow-right" /></Link></div>
      {savedProducts.length ? <>
        <div className="wishlist-toolbar"><strong>Saved products <span>({count})</span></strong><button className="wishlist-clear" onClick={() => setClearWishlistOpen(true)}>Clear Wishlist</button></div>
        <section className="wishlist-grid" aria-label="Saved products">
          {savedProducts.map((product) => <article className="wishlist-card" key={product.id}>
            <Link href={`/products/${product.slug}`} className="wishlist-image"><span className="discount-badge">{Math.round((1 - product.price / product.oldPrice) * 100)}% OFF</span><img src={product.image} alt={product.name} /></Link>
            <div className="wishlist-card-info"><div className="product-category">{product.categoryLabel}</div><Link href={`/products/${product.slug}`}><h2>{product.name}</h2></Link><div className="wishlist-rating"><span>★</span> {product.rating} · In Stock</div><div className="wishlist-price"><strong>{money(product.price)}</strong><del>{money(product.oldPrice)}</del><span>Save {money(product.oldPrice - product.price)}</span></div><div className="wishlist-actions"><button className="wishlist-cart-button" onClick={() => addToCart(product)}><Icon name="cart" /> Add to Cart</button><button className="wishlist-remove" onClick={() => setItemToRemove(product.id)} aria-label={`Remove ${product.name} from wishlist`}><Icon name="trash" /></button></div></div>
          </article>)}
        </section>
      </> : <section className="wishlist-empty"><div className="wishlist-empty-icon"><Icon name="heart" /></div><h2>Your wishlist is waiting</h2><p>Save the pooja essentials and sacred décor you love, then find them here whenever you are ready.</p><Link href="/products" className="primary-button">Explore Products <Icon name="arrow-right" /></Link></section>}
    </main>
    <PublicFooter activeNav={nav} wishlistCount={count} cartCount={cartCount} onNavChange={setNav} onWishlist={() => setNav("wishlist")} onProfile={() => notify("Profile opened")} />
    {toast && <div className="toast show">{toast}</div>}
    <RemoveConfirmationModal open={Boolean(itemToRemove)} onCancel={() => setItemToRemove(null)} onConfirm={confirmRemoveItem} />
    <RemoveConfirmationModal open={clearWishlistOpen} title="Clear Wishlist?" message="Are you sure you want to remove all saved items from your wishlist?" confirmLabel="Clear Wishlist" onCancel={() => setClearWishlistOpen(false)} onConfirm={confirmClearWishlist} />
  </>;
}
