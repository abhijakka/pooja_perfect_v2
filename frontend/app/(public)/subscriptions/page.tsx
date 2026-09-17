import type { Metadata } from "next";
import { PageStub } from "../../page-stub";
import { siteConfig } from "../../../config/site";

export const metadata: Metadata = {
  title: "Pooja Subscriptions | PoojaPoint",
  description: "Schedule recurring deliveries for the essentials you use every day.",
  alternates: { canonical: "/subscriptions" },
  openGraph: { type: "website", siteName: siteConfig.name, url: "/subscriptions" },
};

export default function SubscriptionsPage() {
  return <PageStub title="Subscriptions" description="Schedule recurring deliveries for the essentials you use every day." />;
}
