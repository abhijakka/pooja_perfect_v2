export function formatDate(value: string | Date): string { return new Intl.DateTimeFormat("en-IN").format(new Date(value)); }
