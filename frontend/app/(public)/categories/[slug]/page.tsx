import type { Metadata } from "next";
import { PageStub } from "../../../page-stub";
import { siteConfig } from "../../../../config/site";
import { breadcrumbSchema } from "../../../../lib/seo/breadcrumb-schema";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const label = slug.replaceAll("-", " ");
  return {
    title: `${label} | PoojaPoint`,
    description: `Browse ${label} products for your pooja and home.`,
    alternates: { canonical: `/categories/${slug}` },
    openGraph: { type: "website", siteName: siteConfig.name, url: `/categories/${slug}` },
  };
}

export default async function CategoryPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const label = slug.replaceAll("-", " ");
  const jsonLd = { "@context": "https://schema.org", ...breadcrumbSchema(["Home", label]) };
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }} />
      <PageStub title={label} description="Category products will appear here." />
    </>
  );
}
