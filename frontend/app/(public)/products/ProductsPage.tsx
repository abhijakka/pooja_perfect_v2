"use client";

import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useCart } from "../../../hooks/useCart";
import { useWishlist } from "../../../hooks/useWishlist";
import { Icon } from "../../../components/Icon";
import { PublicHeader } from "../../../components/layout/PublicHeader/PublicHeader";
import { PublicFooter } from "../../../components/layout/PublicFooter/PublicFooter";
import { products, type Product } from "../storefront-data";
import { productsApi } from "../../../services/api/products.api";
import { tilt, resetTilt } from "../../../components/product/ProductCard/ProductGrid";

type SortKey = "featured" | "low" | "high" | "rating" | "name";

const sortOptions: { value: SortKey; label: string }[] = [
  { value: "featured", label: "Sort: Featured" },
  { value: "low", label: "Price: Low to High" },
  { value: "high", label: "Price: High to Low" },
  { value: "rating", label: "Customer Rating" },
  { value: "name", label: "Name" },
];

const categoryOptions = [
  ["pooja", "Pooja Essentials"],
  ["idols", "Idols"],
  ["decor", "Decor"],
  ["gifting", "Gifting"],
] as const;

const badgeById: Record<string, string> = {
  diya: "BESTSELLER",
  ganesha: "POPULAR",
  "lotus-diyas": "NEW",
  temple: "PREMIUM",
  gift: "GIFT PICK",
};

function money(value: number) {
  return `₹${value.toLocaleString("en-IN")}`;
}

export default function ProductsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const categoryParam = searchParams.get("category") || "";
  const [query, setQuery] = useState("");
  const [categories, setCategories] = useState<string[]>(categoryParam ? [categoryParam] : []);
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [minimumRating, setMinimumRating] = useState(0);
  const [stockOnly, setStockOnly] = useState(false);
  const [sort, setSort] = useState<SortKey>("featured");
  const [sortOpen, setSortOpen] = useState(false);
  const { items: cart, count: cartCount, total: cartTotal, addItem, removeItem } = useCart();
  const { count: wishlistCount, contains, toggle } = useWishlist();
  const [cartOpen, setCartOpen] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [toast, setToast] = useState("");
  const [quickProduct, setQuickProduct] = useState<Product | null>(null);
  const [nav, setNav] = useState("products");
  const [catalog, setCatalog] = useState<Product[]>([]);
  const [requestState, setRequestState] = useState<"loading" | "success" | "error">("loading");

  useEffect(() => {
    let active = true;
    productsApi.list({ page: 1, pageSize: 100 }).then(({ products: result }) => {
      if (!active) return;
      setCatalog(result.items.map((item) => ({
        id: item.id,
        name: item.name,
        category: "pooja",
        categoryLabel: "Pooja Essentials",
        price: Number(item.discountPrice ?? item.price),
        oldPrice: Number(item.originalPrice ?? item.price),
        rating: Number(item.averageRating).toFixed(1),
        slug: item.slug,
        image: item.images.find((image) => image.isPrimary)?.url ?? item.images[0]?.url ?? "",
      })));
      setRequestState("success");
    }).catch(() => {
      if (!active) return;
      setCatalog(products);
      setRequestState("error");
    });
    return () => { active = false; };
  }, []);

  // Keep the category filter in sync with the URL (?category=...) so clicking a
  // category in the nav bar updates the listing and breadcrumb.
  const [syncedCategoryParam, setSyncedCategoryParam] = useState(categoryParam);
  if (syncedCategoryParam !== categoryParam) {
    setSyncedCategoryParam(categoryParam);
    setCategories(categoryParam ? [categoryParam] : []);
  }

  useEffect(() => {
    const closeOverlays = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setCartOpen(false);
      setQuickProduct(null);
      setFiltersOpen(false);
    };
    window.addEventListener("keydown", closeOverlays);
    return () => window.removeEventListener("keydown", closeOverlays);
  }, []);

  const notify = (message: string) => setToast(message);
  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(""), 2200);
    return () => window.clearTimeout(timer);
  }, [toast]);
  const filteredProducts = useMemo(() => {
    const min = Number(minPrice) || 0;
    const max = Number(maxPrice) || Infinity;
    return [...catalog]
      .filter((product) => {
        const matchesQuery = `${product.name} ${product.categoryLabel}`.toLowerCase().includes(query.toLowerCase().trim());
        const matchesCategory = !categories.length || categories.includes(product.category);
        return matchesQuery && matchesCategory && product.price >= min && product.price <= max && Number(product.rating) >= minimumRating && (!stockOnly || product.id !== "lotus-diyas");
      })
      .sort((first, second) => {
        if (sort === "low") return first.price - second.price;
        if (sort === "high") return second.price - first.price;
        if (sort === "rating") return Number(second.rating) - Number(first.rating);
        if (sort === "name") return first.name.localeCompare(second.name);
        return 0;
      });
  }, [catalog, categories, maxPrice, minPrice, minimumRating, query, sort, stockOnly]);

  const suggestions = query ? catalog.filter((product) => `${product.name} ${product.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : [];

  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) return notify("Type a product name");
    document.getElementById("products")?.scrollIntoView({ behavior: "smooth" });
  };

  const addToCart = (product: Product) => {
    addItem(product);
    notify("Added to cart");
  };

  const clearFilters = () => {
    setCategories([]);
    setMinPrice("");
    setMaxPrice("");
    setMinimumRating(0);
    setStockOnly(false);
    setQuery("");
    notify("Filters cleared");
  };

  const categoryLabel =
    categories.length === 1
      ? categoryOptions.find(([value]) => value === categories[0])?.[1] ?? "Shop All"
      : "Shop All";

  return (
    <>
      <PublicHeader
        query={query}
        suggestions={suggestions}
        cartCount={cartCount}
        wishlistCount={wishlistCount}
        onQueryChange={setQuery}
        onSearch={submitSearch}
        onProfile={() => notify("Profile opened")}
        onWishlist={() => router.push("/wishlist")}
        onCart={() => router.push("/cart")}
      />
      <div className="breadcrumb"><Link href="/">Home</Link><span>›</span>{categories.length === 1 ? <Link href={`/products?category=${categories[0]}`}>{categoryLabel}</Link> : "Shop All"}</div>
      <main className="products-page" id="products">
        <section className="page-heading">
          <div><div className="heading-eyebrow">PoojaPoint Collection</div><h1>{categories.length === 1 ? categoryLabel : "Shop all products"}</h1><p>Discover thoughtfully selected pooja essentials, idols, diyas, décor and gifting.</p></div>
        </section>
        <section className="shop-layout">
          <aside className={`filters ${filtersOpen ? "mobile-open" : ""}`}>
            <div className="filter-header"><strong>Filters</strong><button className="clear-filter" onClick={clearFilters}>Clear all</button></div>
            <div className="filter-section"><h3>Category</h3>{categoryOptions.map(([value, label]) => <label className="filter-option" key={value}><input type="checkbox" checked={categories.includes(value)} onChange={() => setCategories((items) => items.includes(value) ? items.filter((item) => item !== value) : [...items, value])} />{label}</label>)}</div>
            <div className="filter-section"><h3>Price</h3><div className="price-inputs"><input type="number" value={minPrice} placeholder="Min ₹" onChange={(event) => setMinPrice(event.target.value)} /><input type="number" value={maxPrice} placeholder="Max ₹" onChange={(event) => setMaxPrice(event.target.value)} /></div><button className="apply-price" onClick={() => setFiltersOpen(false)}>Apply</button></div>
            <div className="filter-section"><h3>Customer rating</h3><label className="filter-option"><input type="radio" name="rating" checked={minimumRating === 4} onChange={() => setMinimumRating(4)} />★★★★ & above</label><label className="filter-option"><input type="radio" name="rating" checked={minimumRating === 3} onChange={() => setMinimumRating(3)} />★★★ & above</label></div>
            <div className="filter-section"><h3>Availability</h3><label className="filter-option"><input type="checkbox" checked={stockOnly} onChange={(event) => setStockOnly(event.target.checked)} />In stock only</label></div>
          </aside>
          <div className="shop-content">
            <div className="shop-toolbar"><div className="results">{filteredProducts.length} {filteredProducts.length === 1 ? "product" : "products"}</div><div className="toolbar-right"><button className="mobile-filter" onClick={() => setFiltersOpen(true)}><Icon name="filter" /> Filters</button><div className={`sort-menu ${sortOpen ? "open" : ""}`}><button className="sort-select" type="button" aria-haspopup="listbox" aria-expanded={sortOpen} onClick={() => setSortOpen((open) => !open)}>{sortOptions.find((option) => option.value === sort)?.label}<span className="sort-arrow" /></button>{sortOpen && <div className="sort-options" role="listbox">{sortOptions.map((option) => <button className={`sort-option ${sort === option.value ? "active" : ""}`} type="button" role="option" aria-selected={sort === option.value} key={option.value} onClick={() => { setSort(option.value); setSortOpen(false); }}>{option.label}</button>)}</div>}</div></div></div>
            {requestState === "loading" ? <div className="empty-products">Loading products...</div> : <div className="product-grid">{filteredProducts.map((product) => <article className="product-card" key={product.id} onMouseMove={tilt} onMouseLeave={resetTilt}><div className="product-image">{badgeById[product.id] && <span className="product-badge">{badgeById[product.id]}</span>}<img className="product-photo" src={product.image} alt={product.name} /><button className={`wishlist-button ${contains(product.id) ? "active" : ""}`} onClick={() => toggle(product.id)} aria-label={`Add ${product.name} to wishlist`}><Icon name="heart" /></button><Link className="product-view-button" href={`/products/${product.slug}`}>View product</Link></div><div className="product-info"><div className="product-category">{product.categoryLabel}</div><h2 className="product-title">{product.name}</h2><div className="rating">★★★★★ <span>{product.rating}</span></div><div className="price"><span>{money(product.price)}</span><del className="old-price">{money(product.oldPrice)}</del><span className="discount">{Math.round((1 - product.price / product.oldPrice) * 100)}% off</span></div><div className="card-actions"><button className="add-cart" onClick={() => addToCart(product)}>Add to Cart</button><button className="quick-view" onClick={() => setQuickProduct(product)} aria-label={`Quick view ${product.name}`}><Icon name="eye" /></button></div></div></article>)}</div>}
            {requestState !== "loading" && !filteredProducts.length && <div className="empty-products">{requestState === "error" ? "Backend unavailable. Showing demo products." : "No products match these filters."}</div>}
            <div className="pagination"><button className="page-btn active">1</button><button className="page-btn" onClick={() => notify("More products coming soon")}>2</button><button className="page-btn" onClick={() => notify("More products coming soon")}>3</button><button className="page-btn" onClick={() => notify("More products coming soon")}>→</button></div>
          </div>
        </section>
      </main>
      <PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={cartCount} onNavChange={setNav} onWishlist={() => router.push("/wishlist")} onProfile={() => notify("Profile opened")} />
      {cartOpen && <><button className="cart-overlay show" onClick={() => setCartOpen(false)} aria-label="Close cart" /><aside className="cart open"><div className="cart-head"><h2>Your cart</h2><button className="close-cart" onClick={() => setCartOpen(false)} aria-label="Close cart">×</button></div><div className="cart-items">{cart.length ? cart.map((item) => <div className="cart-item" key={item.id}><button className="remove" onClick={() => removeItem(item.id)}>×</button><strong>{item.name}</strong><div className="cart-item-price">{money(item.price)} × {item.quantity}</div></div>) : <div className="empty">Your cart is empty.</div>}</div><div className="cart-total"><div className="total-row"><span>Total</span><strong>{money(cartTotal)}</strong></div><button className="checkout" onClick={() => notify(cart.length ? "Checkout is ready to connect to your backend" : "Your cart is empty")}>Continue to checkout →</button></div></aside></>}
      {quickProduct && <div className="modal-overlay show" onMouseDown={(event) => { if (event.target === event.currentTarget) setQuickProduct(null); }}><div className="modal product-quick-modal"><button className="modal-close" onClick={() => setQuickProduct(null)} aria-label="Close quick view">×</button><div className="modal-icon"><img src={quickProduct.image} alt="" /></div><span className="modal-label">POOJAPOINT PREMIUM</span><h2>{quickProduct.name}</h2><p>Beautifully curated for your pooja space, everyday rituals, festive moments and gifting.</p><div className="modal-price">{money(quickProduct.price)}</div><button className="modal-buy" onClick={() => { addToCart(quickProduct); setQuickProduct(null); }}>Add to Cart</button></div></div>}
      {toast && <button className="toast show" onClick={() => setToast("")}>{toast}</button>}
    </>
  );
}
