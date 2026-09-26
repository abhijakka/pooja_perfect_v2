import { Icon } from "../../Icon";
import Link from "next/link";
import type { MouseEvent } from "react";

export type StoreProduct = {
  id: string;
  name: string;
  category: string;
  categoryLabel: string;
  price: number;
  oldPrice: number;
  rating: string;
  slug: string;
  image: string;
};

function money(value: number) {
  return `₹${value.toLocaleString("en-IN")}`;
}

type ProductGridProps = {
  products: StoreProduct[];
  wishlist: string[];
  onWishlistToggle: (id: string) => void;
  onAddToCart: (product: StoreProduct) => void;
};

export function tilt(event: MouseEvent<HTMLElement>) {
  const card = event.currentTarget;
  const rect = card.getBoundingClientRect();
  const x = (event.clientX - rect.left) / rect.width - 0.5;
  const y = (event.clientY - rect.top) / rect.height - 0.5;
  card.style.setProperty("--ry", `${(x * 8).toFixed(2)}deg`);
  card.style.setProperty("--rx", `${(-y * 8).toFixed(2)}deg`);
}

export function resetTilt(event: MouseEvent<HTMLElement>) {
  event.currentTarget.style.setProperty("--rx", "0deg");
  event.currentTarget.style.setProperty("--ry", "0deg");
}

export function ProductGrid({ products, wishlist, onWishlistToggle, onAddToCart }: ProductGridProps) {
  return (
    <div className="product-grid">
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
  );
}
