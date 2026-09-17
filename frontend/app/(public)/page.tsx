import type { Metadata } from "next";
import Homepage from "./landingPage";
import { siteConfig } from "../../config/site";

export const metadata: Metadata = {
  title: "PoojaPoint - Premium Pooja Store",
  description: "Beautiful pooja essentials, sacred decor, and thoughtfully curated ritual products.",
  alternates: { canonical: "/" },
  openGraph: { type: "website", siteName: siteConfig.name, url: "/" },
};

export default function HomePage() {
  return <Homepage />;
}