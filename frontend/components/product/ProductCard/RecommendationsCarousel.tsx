"use client";

import { useRef } from "react";
import Link from "next/link";
import { Icon } from "../../Icon";
import { tilt, resetTilt, type StoreProduct } from "./ProductGrid";

type RecommendationsCarouselProps = {
  products: StoreProduct[];
  wishlist: string[];
  onWishlistToggle: (id: string) => void;
  onAddToCart: (product: StoreProduct) => void;
};

function money(value: number) {
  return `₹${value.toLocaleString("en-IN")}`;
}

export function RecommendationsCarousel({ products, wishlist, onWishlistToggle, onAddToCart }: RecommendationsCarouselProps) {
  const trackRef = useRef<HTMLDivElement>(null);

  const scrollByCards = (direction: 1 | -1) => {
    const track = trackRef.current;
    if (!track) return;
    const card = track.querySelector<HTMLElement>(".product-card");
    const step = card ? card.offsetWidth + 17 : track.clientWidth * 0.8;
    track.scrollBy({ left: direction * step, behavior: "smooth" });
  };

  return (
    <section className="recommendations">
      <div className="recommendations-header">
        <h2>You may also like</h2>
        <div className="recommendations-nav">
          <button className="recommend-nav-btn" onClick={() => scrollByCards(-1)} aria-label="Previous products">
            <Icon name="arrow-left" />
          </button>
          <button className="recommend-nav-btn" onClick={() => scrollByCards(1)} aria-label="Next products">
            <Icon name="arrow-right" />
          </button>
        </div>
      </div>
      <div className="recommend-carousel" ref={trackRef}>
        {products.map((product) => (
          <article className="product-card" key={product.id} onMouseMove={tilt} onMouseLeave={resetTilt}>
            <div className="product-image">
              <img className="product-photo" src={product.image} alt={product.name} />
              <button
                className={`wishlist-button ${wishlist.includes(product.id) ? "active" : ""}`}
                onClick={() => onWishlistToggle(product.id)}
                aria-label={`Add ${product.name} to wishlist`}
              >
                <Icon name="heart" />
              </button>
              <Link className="product-view-button" href={`/products/${product.slug}`}>
                View product
              </Link>
            </div>
            <div className="product-info">
              <h3 className="product-title">{product.name}</h3>
              <div className="rating">★★★★★ <span>{product.rating}</span></div>
              <div className="price">
                {money(product.price)} <del className="old-price">{money(product.oldPrice)}</del>
              </div>
              <button className="add-cart" onClick={() => onAddToCart(product)}>
                Add to cart
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}