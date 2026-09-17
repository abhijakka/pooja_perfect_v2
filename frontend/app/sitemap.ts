import type { MetadataRoute } from "next";
import { siteConfig } from "../config/site";
import { products, categories } from "./(public)/storefront-data";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticRoutes = ["", "/products", "/search", "/subscriptions"];
  const productRoutes = products.map((p) => `/products/${p.slug}`);
  const categoryRoutes = categories.map(([slug]) => `/categories/${slug}`);
  const now = new Date();
  return [...staticRoutes, ...productRoutes, ...categoryRoutes].map((path) => ({
    url: `${siteConfig.url}${path === "" ? "/" : path}`,
    lastModified: now,
    changeFrequency: "weekly",
    priority: path === "" ? 1 : 0.8,
  }));
}
