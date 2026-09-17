import type { Metadata } from "next";
import { PageStub } from "../../page-stub";
import { siteConfig } from "../../../config/site";

export const metadata: Metadata = {
  title: "Search Products | PoojaPoint",
  description: "Search for pooja essentials, idols, decor, and more.",
  alternates: { canonical: "/search" },
  openGraph: { type: "website", siteName: siteConfig.name, url: "/search" },
};

export default function SearchPage() {
  return <PageStub title="Search" description="Search results will appear here." />;
}
