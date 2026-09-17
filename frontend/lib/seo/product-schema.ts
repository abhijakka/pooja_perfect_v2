export function productSchema(product: { name: string; price: number }) {
  return { "@type": "Product", name: product.name, offers: { price: product.price, priceCurrency: "INR" } };
}
