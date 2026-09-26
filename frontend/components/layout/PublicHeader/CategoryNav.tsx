"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAppDispatch } from "../../../store/hooks";
import { setOnline } from "../../../store/slices/connectionSlice";
import { categoriesApi, type CategoryDto } from "../../../services/api/categories.api";
import { useAuth } from "../../../hooks/useAuth";

const fallbackCategories = [
  { label: "Home", href: "/" },
  { label: "Shop All", href: "/products" },
  { label: "Pooja Essentials", href: "/products?category=pooja" },
  { label: "Idols", href: "/products?category=idols" },
  { label: "Diyas", href: "/products" },
  { label: "Incense", href: "/products" },
  { label: "Decor", href: "/products?category=decor" },
  { label: "Silver", href: "/products" },
  { label: "Gifting", href: "/products?category=gifting" },
  { label: "Offers", href: "#offers" },
  { label: "Track Order", href: "/order/track" },
] as const;

/** Account navigation is customer-only and must never appear for guests or admins. */
const accountLinks = [
  { label: "My Account", href: "/my-account" },
  { label: "My Orders", href: "/my-orders" },
] as const;

function toNavItem(category: CategoryDto) {
  const slug = category.slug || category.name.toLowerCase().replace(/\s+/g, "-");
  return { label: category.name, href: `/products?category=${encodeURIComponent(slug)}` };
}

export function CategoryNav() {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated } = useAuth();
  const [categories, setCategories] = useState<typeof fallbackCategories>(fallbackCategories);
  const isCustomer = isAuthenticated && user?.role_name === "customer";

  useEffect(() => {
    let active = true;
    categoriesApi.list().then(({ categories: items }) => {
      if (!active) return;
      const mapped = items.length ? items.map(toNavItem) : fallbackCategories;
      setCategories(mapped as typeof fallbackCategories);
      dispatch(setOnline(true));
    }).catch(() => {
      if (!active) return;
      setCategories(fallbackCategories);
      dispatch(setOnline(false));
    });

    return () => {
      active = false;
    };
  }, [dispatch]);

  return (
    <nav className="category-nav" aria-label="Categories">
      {categories.map((item) => (
        <Link href={item.href} key={item.label}>
          {item.label}
        </Link>
      ))}
      {isCustomer &&
        accountLinks.map((item) => (
          <Link href={item.href} key={item.label}>
            {item.label}
          </Link>
        ))}
    </nav>
  );
}
