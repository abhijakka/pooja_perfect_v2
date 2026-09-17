import type { Metadata } from "next";
import { Suspense } from "react";
import ProductsListingPage from "./ProductsPage";
import { siteConfig } from "../../../config/site";

export const metadata: Metadata = {
  title: "All Pooja Products | PoojaPoint",
  description: "Browse our collection of pooja essentials, divine idols, sacred decor, and gifting sets.",
  alternates: { canonical: "/products" },
  openGraph: { type: "website", siteName: siteConfig.name, url: "/products" },
};

export default function ProductsPage() {
  return (
    <Suspense>
      <ProductsListingPage />
    </Suspense>
  );
}
