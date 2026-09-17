import type { CartItem } from "./cart";
export type OrderStatus = "pending" | "confirmed" | "shipped" | "delivered" | "cancelled";
export type Order = { id: string; items: CartItem[]; status: OrderStatus; total: number };
