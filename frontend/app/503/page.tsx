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

export default function ServiceUnavailablePage() {
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
      <main className="gateway-page">
        <section className="gateway-container" aria-labelledby="gateway-title">
          <div className="blob blob-one" aria-hidden="true" />
          <div className="blob blob-two" aria-hidden="true" />
          <div className="gateway-art" aria-hidden="true">
            <div className="gateway">
              <div className="node"><span className="node-dot" /><span className="node-line" /><span className="node-line" /></div>
              <div className="connection" />
              <div className="node"><span className="node-dot" /><span className="node-line" /><span className="node-line" /></div>
            </div>
          </div>
          <div className="status-pill"><span className="status-dot" />Service temporarily unavailable</div>
          <div className="error-code" aria-label="503">5<span>0</span>3</div>
          <div className="content">
            <div className="eyebrow">PoojaPoint</div>
            <h1 id="gateway-title">Service unavailable.</h1>
            <p className="description">PoojaPoint is temporarily unable to connect to the server. Your account, cart and order information are safe.</p>
            <div className="info-card">
              <div className="info-icon"><Icon name="refresh" /></div>
              <div className="info-text"><strong>We&apos;re working on the connection.</strong><span>Please wait a moment and try again. This is usually a temporary server issue.</span></div>
            </div>
            <div className="actions">
              <button className="primary-btn" id="retryButton" onClick={retryPage} disabled={retrying}><Icon name="refresh" />{retrying ? "Connecting..." : "Try Again"}</button>
              <Link className="secondary-btn" href="/"><Icon name="home" />Back to Home</Link>
              <Link className="secondary-btn" href="/products">Continue Shopping</Link>
            </div>
            <div className="help">If the problem continues, <Link href="/chat">contact PoojaPoint Support</Link></div>
          </div>
        </section>
      </main>
      <PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={cartCount} onNavChange={setNav} onWishlist={() => window.location.assign("/wishlist")} onProfile={() => window.location.assign("/my-account")} />
    </>
  );
}
