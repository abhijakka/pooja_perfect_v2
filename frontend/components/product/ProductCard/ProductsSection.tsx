import { ProductGrid, type StoreProduct } from "./ProductGrid";
import Link from "next/link";

type ProductsSectionProps = {
  filter: string;
  products: StoreProduct[];
  wishlist: string[];
  onFilterChange: (filter: string) => void;
  onWishlistToggle: (id: string) => void;
  onAddToCart: (product: StoreProduct) => void;
};

const filters = [
  ["all", "All"],
  ["pooja", "Pooja"],
  ["idols", "Idols"],
  ["decor", "Decor"],
  ["gifting", "Gifting"],
] as const;

export function ProductsSection({ filter, products, wishlist, onFilterChange, onWishlistToggle, onAddToCart }: ProductsSectionProps) {
  return (
    <section className="section" id="products">
      <div className="section-header">
        <h2 className="section-title">Customer favourites</h2>
        <Link className="section-link" href="/products">See all →</Link>
      </div>
      <div className="toolbar">
        {filters.map(([key, label]) => (
          <button className={`filter-btn ${filter === key ? "active" : ""}`} onClick={() => onFilterChange(key)} key={key}>
            {label}
          </button>
        ))}
      </div>
      <ProductGrid products={products} wishlist={wishlist} onWishlistToggle={onWishlistToggle} onAddToCart={onAddToCart} />
    </section>
  );
}
