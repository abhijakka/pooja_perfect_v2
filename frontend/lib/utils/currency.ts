export function formatCurrency(value: number): string { return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(value); }
