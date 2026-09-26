"use client";

import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Icon } from "../../components/Icon";
import { PublicHeader } from "../../components/layout/PublicHeader/PublicHeader";
import { PublicFooter } from "../../components/layout/PublicFooter/PublicFooter";
import { SubscriptionSection } from "../../components/subscription/SubscriptionSection";
import { OfferBanner } from "../../components/layout/OfferBanner";
import { TrustSection } from "../../components/layout/TrustSection";
import { HeroSection, type HeroSlide } from "../../components/layout/HeroSection";
import { CategoriesSection } from "../../components/layout/CategoriesSection";
import { ProductsSection } from "../../components/product/ProductCard/ProductsSection";
import { useCart } from "../../hooks/useCart";
import { useWishlist } from "../../hooks/useWishlist";
import { categoriesApi, type CategoryDto } from "../../services/api/categories.api";
import { heroesApi, type PublicHero } from "../../services/api/hero.api";
import { productsApi } from "../../services/api/products.api";
import { useAppDispatch } from "../../store/hooks";
import { setOnline } from "../../store/slices/connectionSlice";
import { categories, deliveryTimes, payGoProducts, plans, products, toStorefrontProduct, type PayGoProduct, type PlanKey, type Product } from "./storefront-data";

/* Static catalog data is kept in storefront-data.ts. */
/*
  {
    id: "diya",
    name: "Premium Brass Pooja Diya",
    category: "pooja",
    categoryLabel: "Pooja Essentials",
    price: 349,
    oldPrice: 499,
    rating: "4.9",
    slug: "premium-brass-pooja-diya",
    image:
      "https://cdn.shopify.com/s/files/1/0901/3588/8184/files/LaxmiCharanDiyapair_2.png?v=1759706413&width=600",
  },
  {
    id: "ganesha",
    name: "Elegant Ganesha Idol",
    category: "idols",
    categoryLabel: "Divine Idols",
    price: 799,
    oldPrice: 999,
    rating: "4.8",
    slug: "elegant-ganesha-idol",
    image:
      "https://cdn.shopify.com/s/files/1/1857/6931/products/qFQv7mwH9F.jpg?v=1759383512",
  },
  {
    id: "thali",
    name: "Traditional Pooja Thali Set",
    category: "pooja",
    categoryLabel: "Pooja Essentials",
    price: 649,
    oldPrice: 899,
    rating: "4.9",
    slug: "traditional-pooja-thali-set",
    image:
      "https://cdn.shopify.com/s/files/1/0901/3588/8184/files/BrassPoojaThaliwithEngravedFloralDesign.png?v=1772623392&width=600",
  },
  {
    id: "lotus-diyas",
    name: "Lotus Decorative Diyas",
    category: "decor",
    categoryLabel: "Diyas",
    price: 299,
    oldPrice: 399,
    rating: "4.7",
    slug: "lotus-decorative-diyas",
    image:
      "https://cdn.shopify.com/s/files/1/0727/4210/9475/files/IMG_1245.jpg?v=1728130004&width=600",
  },
  {
    id: "kit",
    name: "Daily Pooja Essentials Kit",
    category: "pooja",
    categoryLabel: "Pooja Essentials",
    price: 549,
    oldPrice: 699,
    rating: "4.8",
    slug: "daily-pooja-essentials-kit",
    image:
      "https://cdn.shopify.com/s/files/1/0727/4210/9475/files/IMG_1297.jpg?v=1728298093&width=600",
  },
  {
    id: "temple",
    name: "Premium Temple Decor Set",
    category: "decor",
    categoryLabel: "Sacred Decor",
    price: 899,
    oldPrice: 1199,
    rating: "4.8",
    slug: "premium-temple-decor-set",
    image:
      "https://cdn.shopify.com/s/files/1/0727/4210/9475/files/IMG_1294_1.jpg?v=1728298723&width=600",
  },
  {
    id: "gift",
    name: "Divine Lotus Gift Set",
    category: "gifting",
    categoryLabel: "Gifting",
    price: 699,
    oldPrice: 899,
    rating: "4.9",
    slug: "divine-lotus-gift-set",
    image:
      "https://cdn.shopify.com/s/files/1/0901/3588/8184/files/Shri_Mahalaxmi_Pooja_Box.jpg?v=1753480056&width=600",
  },
  {
    id: "temple-diya",
    name: "Brass Temple Diya Set",
    category: "pooja",
    categoryLabel: "Pooja Essentials",
    price: 449,
    oldPrice: 599,
    rating: "4.8",
    slug: "brass-temple-diya-set",
    image:
      "https://www.brassgiftonline.com/s/5fa28c32f990d2c26c566c66/6a0578cd018449c74ea35c2c/bs1785-g-480x480.jpg",
  },
];

const payGoProducts: PayGoProduct[] = [
  ...products.map(({ id, name, categoryLabel: category, price, image }) => ({
    id,
    name,
    category,
    price,
    image,
  })),
  {
    id: "flowers",
    name: "Fresh Pooja Flowers",
    category: "Fresh Pooja",
    price: 69,
  },
  {
    id: "banana",
    name: "Banana - 6 Pieces",
    category: "Fresh Pooja",
    price: 30,
  },
  { id: "coconut", name: "Fresh Coconut", category: "Fresh Pooja", price: 35 },
  {
    id: "kumkuma",
    name: "Kumkuma & Pasupu",
    category: "Pooja Essentials",
    price: 39,
  },
  {
    id: "agarbatti",
    name: "Premium Agarbatti",
    category: "Pooja Essentials",
    price: 99,
  },
];

const plans: Record<
  PlanKey,
  { name: string; price: number; kind: "date" | "weekday"; count: number }
> = {
  "1_day": { name: "1 Day Pack", price: 49, kind: "date", count: 1 },
  "2_days": { name: "2 Days Pack", price: 98, kind: "date", count: 2 },
  monthly_1_day: {
    name: "1 Month - 1 Day",
    price: 49,
    kind: "weekday",
    count: 1,
  },
  monthly_2_days: {
    name: "1 Month - 2 Days",
    price: 98,
    kind: "weekday",
    count: 2,
  },
};

const deliveryTimes = [
  ["immediate", "Immediately", "Available now · 6:00 AM - 6:00 PM", "⚡"],
  ["06:00-09:00", "Early Morning", "6:00 AM - 9:00 AM", "🌅"],
  ["09:00-12:00", "Morning", "9:00 AM - 12:00 PM", "☀️"],
  ["12:00-15:00", "Afternoon", "12:00 PM - 3:00 PM", "🌤️"],
  ["15:00-18:00", "Evening", "3:00 PM - 6:00 PM", "🌇"],
] as const;

const categories = [
  ["diya", "Pooja Essentials", "120+ products"],
  ["om", "Divine Idols", "80+ products"],
  ["flower", "Festive Decor", "60+ products"],
  ["lotus", "Pooja Kits", "40+ products"],
  ["temple", "Temple Decor", "35+ products"],
  ["heart", "Gifting", "50+ products"],
] as const;
*/

function today() {
  return new Date().toISOString().slice(0, 10);
}
function money(value: number) {
  return `₹${value.toLocaleString("en-IN")}`;
}

export default function Storefront() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [categoryRows, setCategoryRows] = useState<readonly (readonly [string, string, string])[]>(categories);
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>(products);
  const [heroSlides, setHeroSlides] = useState<HeroSlide[]>([]);
  const { items: cart, count: cartCount, total: cartTotal, addItem, removeItem } = useCart();
  const { items: wishlist, count: wishlistCount, toggle } = useWishlist();
  const [cartOpen, setCartOpen] = useState(false);
  const [modal, setModal] = useState<"plan" | "paygo" | null>(null);
  const [plan, setPlan] = useState<PlanKey | null>(null);
  const [dates, setDates] = useState<string[]>([]);
  const [weekdays, setWeekdays] = useState<string[]>([]);
  const [deliveryTime, setDeliveryTime] = useState("");
  const [payGoQuery, setPaygoQuery] = useState("");
  const [selectedPaygo, setSelectedPaygo] = useState<
    (PayGoProduct & { quantity: number })[]
  >([]);
  const [toast, setToast] = useState("");
  const [nav, setNav] = useState("home");

  useEffect(() => {
    let active = true;
    Promise.allSettled([
      categoriesApi.list(),
      productsApi.featured({ page: 1, pageSize: 8 }),
      heroesApi.list(),
    ]).then(([categoriesResult, productsResult, heroesResult]) => {
      if (!active) return;
      if (categoriesResult.status === "fulfilled" && categoriesResult.value.categories?.length) {
        const next = categoriesResult.value.categories.map((category: CategoryDto, index: number) => {
          const icon = ["diya", "om", "flower", "lotus", "temple", "heart"][index % 6] ?? "diya";
          return [icon, category.name, "Curated picks"] as const;
        });
        setCategoryRows(next);
      } else {
        setCategoryRows(categories);
      }

      if (productsResult.status === "fulfilled" && productsResult.value.products?.items?.length) {
        setFeaturedProducts(productsResult.value.products.items.map((item) => toStorefrontProduct(item)));
        dispatch(setOnline(true));
      } else {
        setFeaturedProducts(products);
        dispatch(setOnline(false));
      }

      if (heroesResult.status === "fulfilled" && heroesResult.value.heroes?.length) {
        setHeroSlides(heroesResult.value.heroes.map((hero) => {
          const image = hero.images.find((item) => item.isPrimary) ?? hero.images[0];
          return {
            title: hero.title,
            subtitle: hero.subtitle ?? "",
            badge: hero.badge ?? "",
            accent: hero.accent ?? "rose",
            ctaLabel: hero.ctaLabel ?? "Shop now",
            ctaUrl: hero.ctaLink ?? undefined,
            mediaUrl: image?.url ?? undefined,
            mediaType: image?.mediaType === "video" ? "video" : "image",
            altText: image?.altText ?? undefined,
          };
        }));
      } else {
        // Rendering with an empty slide list falls back to the built-in
        // storefront hero (kept for the offline / not-configured case).
        setHeroSlides([]);
      }
    }).catch(() => {
      if (!active) return;
      setCategoryRows(categories);
      setFeaturedProducts(products);
      setHeroSlides([]);
      dispatch(setOnline(false));
    });

    return () => {
      active = false;
    };
  }, [dispatch]);

  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(""), 2300);
    return () => window.clearTimeout(timer);
  }, [toast]);
  useEffect(() => {
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setCartOpen(false);
        setModal(null);
      }
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, []);

  const filteredProducts = useMemo(
    () =>
      featuredProducts.filter(
        (product) =>
          (filter === "all" || product.category === filter) &&
          (!query ||
            `${product.name} ${product.categoryLabel}`
              .toLowerCase()
              .includes(query.toLowerCase())),
      ),
    [featuredProducts, filter, query],
  );
  const suggestions = useMemo(
    () =>
      query
        ? featuredProducts
            .filter((product) =>
              `${product.name} ${product.categoryLabel}`
                .toLowerCase()
                .includes(query.toLowerCase()),
            )
            .slice(0, 6)
        : [],
    [featuredProducts, query],
  );
  const paygoTotal = selectedPaygo.reduce(
    (total, item) => total + item.price * item.quantity,
    0,
  );
  const immediateAvailable =
    new Date().getHours() >= 6 && new Date().getHours() < 18;
  const activePlan = plan
    ? plans[plan]
    : { name: "", price: 0, kind: "date" as const, count: 0 };
  const formValid = Boolean(
    plan &&
    deliveryTime &&
    (activePlan?.kind === "date"
      ? dates.length === activePlan.count
      : weekdays.length === activePlan?.count) &&
    (modal === "plan" || selectedPaygo.length),
  );

  const notify = (message: string) => setToast(message);
  const addToCart = (product: Product) => {
    addItem(product);
    notify("Added to cart");
  };
  const openPlan = (key: PlanKey) => {
    setPlan(key);
    setDates([]);
    setWeekdays([]);
    setDeliveryTime("");
    setModal("plan");
  };
  const openPaygo = () => {
    setPlan(null);
    setDates([]);
    setWeekdays([]);
    setDeliveryTime("");
    setSelectedPaygo([]);
    setPaygoQuery("");
    setModal("paygo");
  };
  const selectPaygoProduct = (product: PayGoProduct) =>
    setSelectedPaygo((items) => {
      const existing = items.find((item) => item.id === product.id);
      return existing
        ? items.map((item) =>
            item.id === product.id
              ? { ...item, quantity: item.quantity + 1 }
              : item,
          )
        : [...items, { ...product, quantity: 1 }];
    });
  const chooseDate = (index: number, value: string) =>
    setDates((items) => {
      const next = [...items];
      next[index] = value;
      return next
        .filter(Boolean)
        .filter((item, position, all) => all.indexOf(item) === position);
    });
  const chooseWeekday = (index: number, value: string) =>
    setWeekdays((items) => {
      const next = [...items];
      next[index] = value;
      return next
        .filter(Boolean)
        .filter((item, position, all) => all.indexOf(item) === position);
    });
  const submitSearch = (event: FormEvent) => {
    event.preventDefault();
    if (!query) return notify("Type a product name");
    document.getElementById("products")?.scrollIntoView({ behavior: "smooth" });
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
        onProfile={() => notify("Profile opened")}
        onWishlist={() => router.push("/wishlist")}
        onCart={() => router.push("/cart")}
      />

      <main id="top">
        <HeroSection
          slides={heroSlides.length ? heroSlides : undefined}
          onExplore={() => document.getElementById("products")?.scrollIntoView({ behavior: "smooth" })}
        />
        <CategoriesSection categories={categoryRows} />
        <ProductsSection
          filter={filter}
          products={filteredProducts}
          wishlist={wishlist}
          onFilterChange={setFilter}
          onWishlistToggle={toggle}
          onAddToCart={addToCart}
        />

        <SubscriptionSection
          onPlanSelect={(key) => openPlan(key as PlanKey)}
          onPayGoSelect={openPaygo}
          modalProps={{
            open: Boolean(modal),
            payGo: modal === "paygo",
            plan,
            plans,
            products: payGoProducts,
            selectedProducts: selectedPaygo,
            payGoQuery,
            dates,
            weekdays,
            deliveryTime,
            immediateAvailable,
            valid: formValid,
            onClose: () => setModal(null),
            onProductSearch: setPaygoQuery,
            onAddProduct: selectPaygoProduct,
            onDecreaseProduct: (id) => setSelectedPaygo((items) => items.map((item) => item.id === id ? { ...item, quantity: item.quantity - 1 } : item)),
            onRemoveProduct: (id) =>
              setSelectedPaygo((items) =>
                items.filter((item) => item.id !== id),
              ),
            onClearProducts: () => setSelectedPaygo([]),
            onPlanSelect: (key) => {
              if (!selectedPaygo.length)
                return notify("Select at least one product");
              setPlan(key);
              setDates([]);
              setWeekdays([]);
            },
            onDateChange: chooseDate,
            onWeekdayChange: chooseWeekday,
            onDeliveryTime: setDeliveryTime,
            onConfirm: () => {
              function countWeekdaysInMonth(weekdayIndex: number): number {
                const now = new Date();
                const year = now.getFullYear();
                const month = now.getMonth();
                const daysInMonth = new Date(year, month + 1, 0).getDate();
                let count = 0;
                for (let day = 1; day <= daysInMonth; day++) {
                  if (new Date(year, month, day).getDay() === weekdayIndex) {
                    count++;
                  }
                }
                return count;
              }
              function getMultiplier(): number {
                if (!plan) return 1;
                if (plan === "1_day") return 1;
                if (plan === "2_days") return 2;
                if (plan === "monthly_1_day") {
                  const w = weekdays[0];
                  return w ? countWeekdaysInMonth(Number(w)) : 1;
                }
                if (plan === "monthly_2_days") {
                  const w1 = weekdays[0];
                  const w2 = weekdays[1];
                  const c1 = w1 ? countWeekdaysInMonth(Number(w1)) : 0;
                  const c2 = w2 ? countWeekdaysInMonth(Number(w2)) : 0;
                  return c1 + c2;
                }
                return 1;
              }
              const multiplier = getMultiplier();
              if (modal === "plan" && plan) {
                const activePlan = plans[plan];
                addItem(
                  {
                    id: `sub-${plan}-${Date.now()}`,
                    name: `${activePlan.name} Subscription`,
                    price: activePlan.price,
                    oldPrice: activePlan.price,
                    rating: "5.0",
                    category: "subscription",
                    categoryLabel: "Subscriptions",
                    slug: `subscription-${plan}`,
                    image: "",
                  },
                  1,
                );
              } else if (modal === "paygo") {
                for (const product of selectedPaygo) {
                  const total = product.price * multiplier;
                  addItem(
                    {
                      id: product.id,
                      name: product.name,
                      price: total,
                      oldPrice: total,
                      rating: "5.0",
                      category: product.category,
                      categoryLabel: "Pay As You Go",
                      slug: product.id,
                      image: product.image || "",
                    },
                    product.quantity,
                  );
                }
              }
              notify("Added to cart!");
              setModal(null);
            },
          }}
        />

        <OfferBanner />
        <TrustSection />
        
      </main>

      <PublicFooter
        activeNav={nav}
        wishlistCount={wishlistCount}
        cartCount={cartCount}
        onNavChange={setNav}
        onWishlist={() => router.push("/wishlist")}
        onProfile={() => notify("Profile opened")}
      />

      {cartOpen && (
        <>
          <button
            className="cart-overlay show"
            onClick={() => setCartOpen(false)}
            aria-label="Close cart"
          />
          <aside className="cart open">
            <div className="cart-head">
              <h2>Your cart</h2>
              <button
                className="close-cart"
                onClick={() => setCartOpen(false)}
                aria-label="Close cart"
              >
                ×
              </button>
            </div>
            <div className="cart-items">
              {cart.length === 0 ? (
                <div className="empty">Your cart is empty.</div>
              ) : (
                cart.map((item) => (
                  <div className="cart-item" key={item.id}>
                    <button
                      className="remove"
                      onClick={() =>
                        removeItem(item.id)
                      }
                    >
                      ×
                    </button>
                    <strong>{item.name}</strong>
                    <div className="cart-item-price">
                      {money(item.price)} × {item.quantity}
                    </div>
                  </div>
                ))
              )}
            </div>
            <div className="cart-total">
              <div className="total-row">
                <span>Total</span>
                <strong>{money(cartTotal)}</strong>
              </div>
              <button
                className="checkout"
                onClick={() =>
                  notify("Checkout is ready to connect to your backend")
                }
              >
                Continue to checkout →
              </button>
            </div>
          </aside>
        </>
      )}

      {false && modal && (
        <div
          className="modal-overlay show"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setModal(null);
          }}
        >
          <div className="modal">
            <button
              className="modal-close"
              onClick={() => setModal(null)}
              aria-label="Close"
            >
              ×
            </button>
            <div className="modal-icon">
              <Icon name="sparkle" />
            </div>
            <span className="modal-label">CUSTOMIZE YOUR DELIVERY</span>
            <h2>
              {modal === "paygo" ? "Build your own pack" : activePlan?.name}
            </h2>
            <p className="modal-subtitle">
              {modal === "paygo"
                ? "Search products, select multiple items and choose your delivery schedule."
                : "Select your preferred delivery schedule."}
            </p>
            {modal === "paygo" && (
              <div className="paygo-box">
                <div className="paygo-title">1. Search & choose products</div>
                <p className="paygo-help">
                  Search any product and add multiple products to your custom
                  pack.
                </p>
                <div className="paygo-search">
                  <Icon name="search" />
                  <input
                    value={payGoQuery}
                    onChange={(event) => setPaygoQuery(event.target.value)}
                    placeholder="Search diya, flower, coconut..."
                  />
                  <button type="button" onClick={() => setPaygoQuery("")}>
                    ×
                  </button>
                </div>
                <div className="paygo-product-results">
                  {payGoProducts
                    .filter((item) =>
                      `${item.name} ${item.category}`
                        .toLowerCase()
                        .includes(payGoQuery.toLowerCase()),
                    )
                    .map((item) => (
                      <div className="paygo-product-card" key={item.id}>
                        {item.image ? (
                          <img src={item.image} alt={item.name} />
                        ) : (
                          <div className="paygo-product-image">
                            <Icon name="flower" />
                          </div>
                        )}
                        <div className="paygo-product-info">
                          <strong>{item.name}</strong>
                          <small>{item.category}</small>
                          <b>{money(item.price)}</b>
                        </div>
                        <button
                          className="paygo-add"
                          onClick={() => selectPaygoProduct(item)}
                        >
                          +
                        </button>
                      </div>
                    ))}
                </div>
                <div className="selected-products-section">
                  <div className="selected-products-head">
                    <strong>
                      Selected products{" "}
                      <small>
                        {selectedPaygo.reduce(
                          (sum, item) => sum + item.quantity,
                          0,
                        )}{" "}
                        items
                      </small>
                    </strong>
                    <button
                      className="clear-products"
                      onClick={() => setSelectedPaygo([])}
                    >
                      Clear all
                    </button>
                  </div>
                  {selectedPaygo.length === 0 ? (
                    <div className="no-products">
                      🛍️<p>No products selected yet</p>
                      <small>Search above and tap +</small>
                    </div>
                  ) : (
                    selectedPaygo.map((item) => (
                      <div className="selected-paygo-item" key={item.id}>
                        <div className="selected-paygo-info">
                          <strong>{item.name}</strong>
                          <small>
                            {money(item.price)} × {item.quantity}
                          </small>
                        </div>
                        <div className="quantity-control">
                          <button
                            onClick={() =>
                              setSelectedPaygo((items) =>
                                items.flatMap((current) =>
                                  current.id === item.id
                                    ? current.quantity > 1
                                      ? [
                                          {
                                            ...current,
                                            quantity: current.quantity - 1,
                                          },
                                        ]
                                      : []
                                    : [current],
                                ),
                              )
                            }
                          >
                            -
                          </button>
                          <span>{item.quantity}</span>
                          <button onClick={() => selectPaygoProduct(item)}>
                            +
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
                <div className="paygo-title paygo-plan-title">
                  2. Choose delivery plan
                </div>
              </div>
            )}
            {modal === "paygo" && (
              <div className="paygo-plans">
                {(Object.keys(plans) as PlanKey[]).map((key) => (
                  <button
                    className={`paygo-option ${plan === key ? "active" : ""}`}
                    onClick={() => {
                      if (!selectedPaygo.length)
                        return notify("Select at least one product");
                      setPlan(key);
                      setDates([]);
                      setWeekdays([]);
                    }}
                    key={key}
                  >
                    <strong>{plans[key].name}</strong>
                    <small>
                      {plans[key].kind === "date"
                        ? `Choose ${plans[key].count} exact date${plans[key].count > 1 ? "s" : ""}`
                        : `Choose ${plans[key].count} weekday${plans[key].count > 1 ? "s" : ""}`}
                    </small>
                  </button>
                ))}
              </div>
            )}
            <div className="selected-plan">
              <div>
                <small>SELECTED PLAN</small>
                <strong>{activePlan?.name ?? "Choose a delivery plan"}</strong>
              </div>
              <b>
                {modal === "paygo" && plan
                  ? money(
                      paygoTotal *
                        (plan === "2_days" || plan === "monthly_2_days"
                          ? 2
                          : 1),
                    )
                  : activePlan
                    ? money(activePlan.price)
                    : "₹-"}
              </b>
            </div>
            {activePlan && (
              <div className="date-section">
                <label>
                  {activePlan.kind === "date"
                    ? "Select your delivery date"
                    : "Choose your delivery weekday"}
                </label>
                <div className="date-fields">
                  {Array.from({ length: activePlan.count }, (_, index) =>
                    activePlan.kind === "date" ? (
                      <input
                        className="date-input"
                        type="date"
                        min={today()}
                        value={dates[index] ?? ""}
                        onChange={(event) =>
                          chooseDate(index, event.target.value)
                        }
                        key={index}
                      />
                    ) : (
                      <select
                        className="weekday-select"
                        value={weekdays[index] ?? ""}
                        onChange={(event) =>
                          chooseWeekday(index, event.target.value)
                        }
                        key={index}
                      >
                        <option value="">Select weekday</option>
                        {[
                          "Sunday",
                          "Monday",
                          "Tuesday",
                          "Wednesday",
                          "Thursday",
                          "Friday",
                          "Saturday",
                        ].map((day, dayIndex) => (
                          <option value={String(dayIndex)} key={day}>
                            {day}
                          </option>
                        ))}
                      </select>
                    ),
                  )}
                </div>
                <div className="date-preview">
                  {(activePlan.kind === "date" ? dates : weekdays).length
                    ? (activePlan.kind === "date" ? dates : weekdays).map(
                        (value) => (
                          <span className="date-chip" key={value}>
                            {activePlan.kind === "date"
                              ? new Date(
                                  `${value}T00:00:00`,
                                ).toLocaleDateString("en-IN", {
                                  day: "numeric",
                                  month: "short",
                                  year: "numeric",
                                })
                              : [
                                  "Sunday",
                                  "Monday",
                                  "Tuesday",
                                  "Wednesday",
                                  "Thursday",
                                  "Friday",
                                  "Saturday",
                                ][Number(value)]}
                          </span>
                        ),
                      )
                    : "Choose your delivery schedule."}
                </div>
              </div>
            )}
            <div className="delivery-time-section">
              <div className="delivery-time-head">
                <label className="delivery-time-title">
                  When should we deliver?
                </label>
                <span className="delivery-time-required">REQUIRED</span>
              </div>
              <p className="delivery-time-help">
                Choose Immediate delivery or a preferred time window. Delivery
                service is open daily from 6:00 AM to 6:00 PM.
              </p>
              <div className="delivery-time-options">
                {deliveryTimes.map(([value, label, description, icon]) => (
                  <button
                    className={`delivery-time-option ${deliveryTime === value ? "active" : ""}`}
                    disabled={value === "immediate" && !immediateAvailable}
                    onClick={() => setDeliveryTime(value)}
                    key={value}
                  >
                    <span className="delivery-time-icon">{icon}</span>
                    <strong>{label}</strong>
                    <small>
                      {value === "immediate" && !immediateAvailable
                        ? "Available daily from 6:00 AM - 6:00 PM"
                        : description}
                    </small>
                  </button>
                ))}
              </div>
              <div className="selected-delivery-time">
                {deliveryTime
                  ? deliveryTimes.find(([value]) => value === deliveryTime)?.[2]
                  : "Please select a delivery time."}
              </div>
            </div>
            <button
              className="confirm"
              disabled={!formValid}
              onClick={() => {
                notify("Subscription ready for checkout");
                setModal(null);
              }}
            >
              Continue to checkout
            </button>
          </div>
        </div>
      )}
      {toast && <div className="toast show">{toast}</div>}
    </>
  );
}
