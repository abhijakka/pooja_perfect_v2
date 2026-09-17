export function breadcrumbSchema(items: string[]) { return { "@type": "BreadcrumbList", itemListElement: items.map((name, position) => ({ "@type": "ListItem", name, position: position + 1 })) }; }
