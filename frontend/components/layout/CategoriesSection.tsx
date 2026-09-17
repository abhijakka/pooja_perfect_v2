import { CategoryGrid } from "./CategoryGrid";
import Link from "next/link";

type CategoriesSectionProps = {
  categories: readonly (readonly [string, string, string])[];
};

export function CategoriesSection({ categories }: CategoriesSectionProps) {
  return (
    <section className="section" id="categories">
      <div className="section-header">
        <h2 className="section-title">Shop by category</h2>
        <Link className="section-link" href="/products">View all →</Link>
      </div>
      <CategoryGrid categories={categories} />
    </section>
  );
}
