import Link from "next/link";

export function Logo() {
  return (
    <Link className="logo" href="/" aria-label="PoojaPoint home">
      Pooja<span>Point</span>
    </Link>
  );
}
