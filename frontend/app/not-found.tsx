"use client";

import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import { Icon } from "../components/Icon";
import { PublicFooter } from "../components/layout/PublicFooter/PublicFooter";
import { PublicHeader } from "../components/layout/PublicHeader/PublicHeader";
import { useCart } from "../hooks/useCart";
import { useWishlist } from "../hooks/useWishlist";
import { products } from "./(public)/storefront-data";

export default function NotFoundPage() {
  const { count: cartCount } = useCart();
  const { count: wishlistCount } = useWishlist();
  const [query, setQuery] = useState("");
  const [nav, setNav] = useState("shop");

  const suggestions = useMemo(
    () => query ? products.filter((item) => `${item.name} ${item.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : [],
    [query],
  );

  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
  };

  return (
    <>
      <PublicHeader
        query={query}
        suggestions={suggestions}
        cartCount={cartCount}
        wishlistCount={wishlistCount}
        onQueryChange={setQuery}
        onSearch={submitSearch}
        onProfile={() => window.location.assign("/my-account")}
        onWishlist={() => window.location.assign("/wishlist")}
        onCart={() => window.location.assign("/cart")}
      />
      <main className="error-page">
        <section className="error-container" aria-labelledby="error-title">
          <div className="blob blob-one" aria-hidden="true" />
          <div className="blob blob-two" aria-hidden="true" />
          <div className="error-art" aria-hidden="true"><Icon name="lotus" /></div>
          <div className="error-number" aria-hidden="true">4<span>0</span>4</div>
          <div className="error-content">
            <div className="eyebrow">PoojaPoint</div>
            <h1 id="error-title">This page wandered away.</h1>
            <p>The page you&apos;re looking for may have moved, been removed, or the link may be incorrect. Let&apos;s take you back to something beautiful.</p>
            <div className="error-actions">
              <Link className="primary-btn" href="/"><Icon name="home" />Back to Home</Link>
              <Link className="secondary-btn" href="/products">Shop Products</Link>
            </div>
          </div>
          <div className="quick-links">
            <div className="quick-links-title">Or explore something else</div>
            <div className="links">
              <Link href="/products">Shop All</Link>
              <Link href="/products?category=pooja">Pooja Essentials</Link>
              <Link href="/products?category=decor">Diyas</Link>
              <Link href="/products?category=idols">Idols</Link>
              <Link href="/products?category=gifting">Gifting</Link>
              <Link href="/products">Offers</Link>
            </div>
          </div>
        </section>
      </main>
      <PublicFooter
        activeNav={nav}
        wishlistCount={wishlistCount}
        cartCount={cartCount}
        onNavChange={setNav}
        onWishlist={() => window.location.assign("/wishlist")}
        onProfile={() => window.location.assign("/my-account")}
      />
    </>
  );
}
