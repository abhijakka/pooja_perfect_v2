import type { Metadata } from "next";
import "./globals.css";
import Providers from "./providers";
import { siteConfig } from "../config/site";

export const metadata: Metadata = {
  metadataBase: new URL(siteConfig.url),
  title: "PoojaPoint - Premium Pooja Store",
  description: "Beautiful pooja essentials, sacred decor, and thoughtfully curated ritual products.",
  openGraph: {
    type: "website",
    siteName: siteConfig.name,
    title: "PoojaPoint - Premium Pooja Store",
    description: "Beautiful pooja essentials, sacred decor, and thoughtfully curated ritual products.",
  },
  twitter: { card: "summary_large_image" },
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" data-scroll-behavior="smooth"><body suppressHydrationWarning><Providers>{children}</Providers></body></html>;
}