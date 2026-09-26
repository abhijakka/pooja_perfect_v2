import type { MetadataRoute } from "next";
import { siteConfig } from "../config/site";
import { categories } from "./(public)/storefront-data";

export default function sitemap(): MetadataRoute.Sitemap {
  // Only routes that always resolve are advertised. Product URLs are served from the
  // backend catalog and are exposed through the product routes the backend returns,
  // not through the demo fallback array.
  const staticRoutes = ["", "/products", "/search", "/subscriptions"];
  const categoryRoutes = categories.map(([slug]) => `/categories/${slug}`);
  const now = new Date();
  return [...staticRoutes, ...categoryRoutes].map((path) => ({
    url: `${siteConfig.url}${path === "" ? "/" : path}`,
    lastModified: now,
    changeFrequency: "weekly",
    priority: path === "" ? 1 : 0.8,
  }));
}
