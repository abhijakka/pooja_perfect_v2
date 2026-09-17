import type { MetadataRoute } from "next";
import { siteConfig } from "../config/site";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: [
        "/cart", "/checkout", "/wishlist", "/chat", "/order",
        "/my-account", "/my-orders", "/addresses", "/security", "/notifications",
        "/login", "/signup", "/otp", "/two-factor",
        "/admin", "/503", "/timeout",
      ],
    },
    sitemap: `${siteConfig.url}/sitemap.xml`,
  };
}
