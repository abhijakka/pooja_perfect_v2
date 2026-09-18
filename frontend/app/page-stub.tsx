import Link from "next/link";

export function PageStub({ title, description }: { title: string; description: string }) { return <main className="shell"><nav><Link href="/">PoojaPoint</Link><Link href="/products">Shop</Link><Link href="/cart">Cart</Link></nav><h1>{title}</h1><p>{description}</p><Link className="button" href="/">Back home</Link></main>; }
