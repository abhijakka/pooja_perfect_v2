import type { Cart } from "../../types/cart";
export const cartStorage = { get: (): Cart => ({ items: [] }), set: (_cart: Cart) => undefined };
