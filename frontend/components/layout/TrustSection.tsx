import { TrustGrid } from "./TrustGrid";

const trustItems = [
  ["truck", "Fast delivery", "Carefully packed and delivered to your doorstep."],
  ["shield", "Secure payments", "Safe and reliable checkout every time."],
  ["lotus", "Curated with care", "Thoughtfully selected products for your sacred space."],
  ["return", "Easy returns", "Simple and customer-friendly return experience."],
] as const;

export function TrustSection() {
  return (
    <section className="section">
      <TrustGrid items={trustItems} />
    </section>
  );
}
