import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { products } from "../../storefront-data";
import { siteConfig } from "../../../../config/site";
import { productSchema } from "../../../../lib/seo/product-schema";
import ProductDetailPage from "./ProductDetailPage";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const product = products.find((item) => item.slug === slug);
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
  const product = products.find((item) => item.slug === slug);
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
