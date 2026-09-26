import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { products, toStorefrontProduct, type Product } from "../../storefront-data";
import { siteConfig } from "../../../../config/site";
import { productSchema } from "../../../../lib/seo/product-schema";
import { categoryNameFor, categorySlugFor, productsApi } from "../../../../services/api/products.api";
import ProductDetailPage from "./ProductDetailPage";

/**
 * Backend first, documented demo catalog second, 404 last. The route segment stays
 * `[slug]` because slug is the product's canonical public identifier. Resolution never
 * depends on a card knowing whether the backend was reachable.
 */
async function loadProduct(slug: string): Promise<Product | null> {
  try {
    const { product, categories } = await productsApi.bySlug(slug);
    if (product) {
      return toStorefrontProduct(
        product,
        {
          slug: categorySlugFor(categories, product.categoryId),
          label: categoryNameFor(categories, product.categoryId),
        },
      );
    }
  } catch {
    // Backend unavailable or no such product — fall through to the demo catalog.
  }
  return products.find((item) => item.slug === slug) ?? null;
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const product = await loadProduct(slug);
  if (!product) return {};
  const description = `${product.name} — ${product.categoryLabel} at ₹${product.price}.`;
  return {
    title: `${product.name} | PoojaPoint`,
    description,
    alternates: { canonical: `/products/${product.slug}` },
    openGraph: { title: product.name, description, type: "website", siteName: siteConfig.name, images: [product.image], url: `/products/${product.slug}` },
  };
}

export default async function ProductPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const product = await loadProduct(slug);
  if (!product) notFound();
  const jsonLd = {
    "@context": "https://schema.org",
    ...productSchema(product),
    image: product.image,
    url: `${siteConfig.url}/products/${product.slug}`,
  };
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }} />
      <ProductDetailPage product={product} />
    </>
  );
}
