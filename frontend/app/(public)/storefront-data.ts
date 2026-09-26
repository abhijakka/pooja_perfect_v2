import type { CatalogProduct } from "../../services/api/products.api";

export type Product = {
  id: string;
  name: string;
  category: string;
  categoryLabel: string;
  price: number;
  oldPrice: number;
  rating: string;
  slug: string;
  image: string;
};

export type CartItem = Product & { quantity: number };
export type PlanKey = "1_day" | "2_days" | "monthly_1_day" | "monthly_2_days";
export type PayGoProduct = {
  id: string;
  name: string;
  category: string;
  price: number;
  image?: string;
};

export const products: Product[] = [
  { id: "diya", name: "Premium Brass Pooja Diya", category: "pooja", categoryLabel: "Pooja Essentials", price: 349, oldPrice: 499, rating: "4.9", slug: "premium-brass-pooja-diya", image: "https://cdn.shopify.com/s/files/1/0901/3588/8184/files/LaxmiCharanDiyapair_2.png?v=1759706413&width=600" },
  { id: "ganesha", name: "Elegant Ganesha Idol", category: "idols", categoryLabel: "Divine Idols", price: 799, oldPrice: 999, rating: "4.8", slug: "elegant-ganesha-idol", image: "https://cdn.shopify.com/s/files/1/1857/6931/products/qFQv7mwH9F.jpg?v=1759383512" },
  { id: "thali", name: "Traditional Pooja Thali Set", category: "pooja", categoryLabel: "Pooja Essentials", price: 649, oldPrice: 899, rating: "4.9", slug: "traditional-pooja-thali-set", image: "https://cdn.shopify.com/s/files/1/0901/3588/8184/files/BrassPoojaThaliwithEngravedFloralDesign.png?v=1772623392&width=600" },
  { id: "lotus-diyas", name: "Lotus Decorative Diyas", category: "decor", categoryLabel: "Diyas", price: 299, oldPrice: 399, rating: "4.7", slug: "lotus-decorative-diyas", image: "https://cdn.shopify.com/s/files/1/0727/4210/9475/files/IMG_1245.jpg?v=1728130004&width=600" },
  { id: "kit", name: "Daily Pooja Essentials Kit", category: "pooja", categoryLabel: "Pooja Essentials", price: 549, oldPrice: 699, rating: "4.8", slug: "daily-pooja-essentials-kit", image: "https://cdn.shopify.com/s/files/1/0727/4210/9475/files/IMG_1297.jpg?v=1728298093&width=600" },
  { id: "temple", name: "Premium Temple Decor Set", category: "decor", categoryLabel: "Sacred Decor", price: 899, oldPrice: 1199, rating: "4.8", slug: "premium-temple-decor-set", image: "https://cdn.shopify.com/s/files/1/0727/4210/9475/files/IMG_1294_1.jpg?v=1728298723&width=600" },
  { id: "gift", name: "Divine Lotus Gift Set", category: "gifting", categoryLabel: "Gifting", price: 699, oldPrice: 899, rating: "4.9", slug: "divine-lotus-gift-set", image: "https://cdn.shopify.com/s/files/1/0901/3588/8184/files/Shri_Mahalaxmi_Pooja_Box.jpg?v=1753480056&width=600" },
  { id: "temple-diya", name: "Brass Temple Diya Set", category: "pooja", categoryLabel: "Pooja Essentials", price: 449, oldPrice: 599, rating: "4.8", slug: "brass-temple-diya-set", image: "https://www.brassgiftonline.com/s/5fa28c32f990d2c26c566c66/6a0578cd018449c74ea35c2c/bs1785-g-480x480.jpg" },
];

export const payGoProducts: PayGoProduct[] = [
  ...products.map(({ id, name, categoryLabel: category, price, image }) => ({ id, name, category, price, image })),
  { id: "flowers", name: "Fresh Pooja Flowers", category: "Fresh Pooja", price: 69 },
  { id: "banana", name: "Banana - 6 Pieces", category: "Fresh Pooja", price: 30 },
  { id: "coconut", name: "Fresh Coconut", category: "Fresh Pooja", price: 35 },
  { id: "kumkuma", name: "Kumkuma & Pasupu", category: "Pooja Essentials", price: 39 },
  { id: "agarbatti", name: "Premium Agarbatti", category: "Pooja Essentials", price: 99 },
];

export const plans: Record<PlanKey, { name: string; price: number; kind: "date" | "weekday"; count: number }> = {
  "1_day": { name: "1 Day Pack", price: 49, kind: "date", count: 1 },
  "2_days": { name: "2 Days Pack", price: 98, kind: "date", count: 2 },
  monthly_1_day: { name: "1 Month - 1 Day", price: 49, kind: "weekday", count: 1 },
  monthly_2_days: { name: "1 Month - 2 Days", price: 98, kind: "weekday", count: 2 },
};

export const deliveryTimes = [
  ["immediate", "Immediately", "Available now · 6:00 AM - 6:00 PM", "⚡"],
  ["06:00-09:00", "Early Morning", "6:00 AM - 9:00 AM", "🌅"],
  ["09:00-12:00", "Morning", "9:00 AM - 12:00 PM", "☀️"],
  ["12:00-15:00", "Afternoon", "12:00 PM - 3:00 PM", "🌤️"],
  ["15:00-18:00", "Evening", "3:00 PM - 6:00 PM", "🌇"],
] as const;

export const categories = [
  ["diya", "Pooja Essentials", "120+ products"],
  ["om", "Divine Idols", "80+ products"],
  ["flower", "Festive Decor", "60+ products"],
  ["lotus", "Pooja Kits", "40+ products"],
  ["temple", "Temple Decor", "35+ products"],
  ["heart", "Gifting", "50+ products"],
] as const;

/**
 * Single mapping from a backend catalog product to the storefront product shape every
 * card, cart row and detail page renders. Backend values win; nothing is hardcoded except
 * the category fallback used when the backend exposes no matching category.
 */
export function toStorefrontProduct(item: CatalogProduct, category?: { slug: string; label: string }): Product {
	const price = Number(item.discountPrice ?? item.price);
	const listPrice = Number(item.originalPrice ?? item.price);
	return {
		id: item.id,
		name: item.name,
		category: category?.slug ?? "pooja",
		categoryLabel: category?.label ?? "Pooja Essentials",
		price: Number.isFinite(price) ? price : 0,
		oldPrice: Number.isFinite(listPrice) ? listPrice : 0,
		rating: Number(item.averageRating ?? 0).toFixed(1),
		slug: item.slug,
		image: item.images?.find((image) => image.isPrimary)?.url ?? item.images?.[0]?.url ?? "",
	};
}
