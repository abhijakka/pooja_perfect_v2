import type { ReactNode } from "react";

type IconName =
  | "search"
  | "user"
  | "heart"
  | "bag"
  | "diya"
  | "lotus"
  | "temple"
  | "flower"
  | "shield"
  | "truck"
  | "return"
  | "chat"
  | "sparkle"
  | "filter"
  | "eye"
  | "tag"
  | "check"
  | "home"
  | "box"
  | "cart"
  | "lock"
  | "trash"
  | "plus"
  | "minus"
  | "arrow-right"
  | "refresh"
  | "headphones"
  | "card"
  | "wallet"
  | "location"
  | "mail"
  | "phone"
  | "eye"
  | "eye-off"
  | "gift"
  | "arrow-left";

const paths: Record<IconName, ReactNode> = {
  search: <><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></>,
  user: <><circle cx="12" cy="8" r="3.5" /><path d="M5 20c.8-4 3.1-6 7-6s6.2 2 7 6" /></>,
  heart: <path d="M20.8 8.8c0 5.2-8.8 10-8.8 10S3.2 14 3.2 8.8A4.8 4.8 0 0 1 12 6.1a4.8 4.8 0 0 1 8.8 2.7Z" />,
  bag: <><path d="M5 8h14l1 12H4L5 8Z" /><path d="M9 9V6a3 3 0 0 1 6 0v3" /></>,
  diya: <><path d="M5 13h14c-.7 4.2-3 6-7 6s-6.3-1.8-7-6Z" /><path d="M12 13c-2-2.2-1.5-4.5 0-6 1.5 1.5 2 3.8 0 6Z" /><path d="M4 20h16" /></>,
  lotus: <><path d="M12 20c-4.5 0-8-2.2-9-5.5 3.2-.4 6.1.5 9 3.5 2.9-3 5.8-3.9 9-3.5-1 3.3-4.5 5.5-9 5.5Z" /><path d="M12 18c-3.2-2.8-4.5-6.2-3.2-10 2.5 1.2 3.2 4.2 3.2 10Zm0 0c3.2-2.8 4.5-6.2 3.2-10-2.5 1.2-3.2 4.2-3.2 10Z" /></>,
  temple: <path d="M3 20h18M5 20V10h14v10M3 10l9-6 9 6M8 20v-6h3v6m5 0v-6h-3v6" />,
  flower: <><circle cx="12" cy="12" r="2.5" /><path d="M12 9C8 7 7 3 10 2c2.5-.8 3.5 3.5 2 7Zm3 3c2-4 6-4 7-1 1 2.5-3.5 4-7 2Zm-3 3c4-2 7 1 6 4-1 2.5-5 1-6-4Zm-3-3c-2 4-6 4-7 1-1-2.5 3.5-4 7-2Z" /></>,
  shield: <><path d="M12 21s8-3.5 8-10V5l-8-3-8 3v6c0 6.5 8 10 8 10Z" /><path d="m9 12 2 2 4-4" /></>,
  truck: <><path d="M3 6h11v11H3zM14 10h4l3 3v4h-7z" /><circle cx="7" cy="19" r="1.5" /><circle cx="18" cy="19" r="1.5" /></>,
  return: <path d="M9 7H4l3-3M4 7c5-5 13-3 15 2 2 5-2 10-7 10-3 0-5-1-7-3" />,
  chat: <path d="M20 11.5a7.5 7.5 0 0 1-8 7.5 9 9 0 0 1-4-.9L3 20l1.8-4.2A7.2 7.2 0 0 1 4 11.5 7.5 7.5 0 0 1 12 4a7.5 7.5 0 0 1 8 7.5Z" />,
  sparkle: <path d="M12 2l1.8 7.2L21 11l-7.2 1.8L12 20l-1.8-7.2L3 11l7.2-1.8Z" />,
  filter: <path d="M4 6h16M7 12h10m-7 6h4" />,
  eye: <><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z" /><circle cx="12" cy="12" r="2.5" /></>,
  tag: <><path d="m20 13-7 7-9-9V4h7l9 9Z" /><circle cx="8" cy="8" r="1" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  home: <><path d="m3 11 9-8 9 8" /><path d="M5 10v10h14V10M9 20v-6h6v6" /></>,
  box: <><path d="m4 7 8-4 8 4-8 4-8-4Z" /><path d="M4 7v10l8 4 8-4V7M12 11v10" /></>,
  cart: <><circle cx="9" cy="20" r="1.5" /><circle cx="18" cy="20" r="1.5" /><path d="M3 4h2l2.4 11.5h11.2L21 8H6" /></>,
  lock: <><rect x="4" y="10" width="16" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></>,
  trash: <><path d="M4 7h16M10 11v6m4-6v6M6 7l1 14h10l1-14M9 7V4h6v3" /></>,
  plus: <path d="M12 5v14M5 12h14" />,
  minus: <path d="M5 12h14" />,
  "arrow-right": <path d="M5 12h14m-6-6 6 6-6 6" />,
  refresh: <><path d="M20 11a8 8 0 0 0-14.5-4L3 10M3 5v5h5" /><path d="M4 13a8 8 0 0 0 14.5 4L21 14M21 19v-5h-5" /></>,
  headphones: <><path d="M4 14v-2a8 8 0 0 1 16 0v2" /><path d="M4 14h3v5H5a1 1 0 0 1-1-1zM20 14h-3v5h2a1 1 0 0 0 1-1z" /></>,
  card: <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="M3 10h18" /><path d="M7 15h4" /></>,
  wallet: <><path d="M4 7h15a2 2 0 0 1 2 2v10H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h13" /><path d="M16 13h5" /><circle cx="16" cy="13" r=".8" /></>,
  location: <><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" /><circle cx="12" cy="10" r="2.5" /></>,
  mail: <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" /></>,
  phone: <path d="M6.5 3h3l1.5 4-2 1.5c1 2.2 2.3 3.5 4.5 4.5l1.5-2 4 1.5v3c0 1.1-.9 2-2 2C9.3 17.5 6.5 14.7 6.5 7c0-1.1.9-2 2-2" />,
  "eye-off": <><path d="M3 3l18 18M10.6 10.6a2 2 0 0 0 2.8 2.8M9.9 5.3A11 11 0 0 1 12 5c6 0 10 7 10 7a18 18 0 0 1-3.1 3.8M6.1 6.1C3.6 8 2 12 2 12s4 7 10 7c1.4 0 2.7-.3 3.9-.9" /></>,
  gift: <><rect x="3" y="10" width="18" height="10" rx="1" /><path d="M12 10v10M3 14h18M12 10H7a2.5 2.5 0 1 1 2.5-2.5C9.5 9 12 10 12 10Zm0 0h5a2.5 2.5 0 1 0-2.5-2.5C14.5 9 12 10 12 10Z" /></>,
  "arrow-left": <path d="M19 12H5m6-6-6 6 6 6" />,
};

export function Icon({ name }: { name: string }) {
  return <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">{paths[name as IconName] ?? paths.sparkle}</svg>;
}
