"use client";

import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import { Icon } from "../../components/Icon";
import { PublicFooter } from "../../components/layout/PublicFooter/PublicFooter";
import { PublicHeader } from "../../components/layout/PublicHeader/PublicHeader";
import { useCart } from "../../hooks/useCart";
import { useWishlist } from "../../hooks/useWishlist";
import { products } from "../(public)/storefront-data";

export default function ServerTimeoutPage() {
  const { count: cartCount } = useCart();
  const { count: wishlistCount } = useWishlist();
  const [query, setQuery] = useState("");
  const [nav, setNav] = useState("shop");
  const [retrying, setRetrying] = useState(false);

  const suggestions = useMemo(
    () => query ? products.filter((item) => `${item.name} ${item.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : [],
    [query],
  );

  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
  };

  const retryPage = () => {
    if (retrying) return;
    setRetrying(true);
    window.setTimeout(() => window.location.reload(), 700);
  };

  return (
    <>
      <PublicHeader query={query} suggestions={suggestions} cartCount={cartCount} wishlistCount={wishlistCount} onQueryChange={setQuery} onSearch={submitSearch} onProfile={() => window.location.assign("/my-account")} onWishlist={() => window.location.assign("/wishlist")} onCart={() => window.location.assign("/cart")} />
      <main className="timeout-page">
        <section className="timeout-container" aria-labelledby="timeout-title">
          <div className="blob blob-one" aria-hidden="true" />
          <div className="blob blob-two" aria-hidden="true" />
          <div className="server-art" aria-hidden="true">
            <div className="server-box"><div className="server-light" /></div>
            <div className="server-base" />
          </div>
          <div className="status-pill"><span className="status-dot" />Server response delayed</div>
          <div className="eyebrow">PoojaPoint</div>
          <h1 id="timeout-title">The server took too long.</h1>
          <p className="description">We couldn&apos;t get a response from the server in time. Your account and order information are safe. Please try again in a moment.</p>
          <div className="retry-box">
            <div className="retry-message"><strong>Nothing is wrong with your account.</strong><span>This usually resolves itself after a quick refresh.</span></div>
            <button className="retry-btn" id="retryButton" onClick={retryPage} disabled={retrying}><Icon name="refresh" />{retrying ? "Retrying..." : "Try again"}</button>
          </div>
          <div className="actions">
            <Link className="primary-btn" href="/"><Icon name="home" />Back to Home</Link>
            <Link className="secondary-btn" href="/products">Continue Shopping</Link>
          </div>
          <div className="help-text">Still having trouble? <Link href="/chat">Contact PoojaPoint Support</Link></div>
        </section>
      </main>
      <PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={cartCount} onNavChange={setNav} onWishlist={() => window.location.assign("/wishlist")} onProfile={() => window.location.assign("/my-account")} />
    </>
  );
}
