import { Icon } from "../Icon";

type CategoryGridProps = {
  categories: readonly (readonly [string, string, string])[];
};

export function CategoryGrid({ categories }: CategoryGridProps) {
  return (
    <div className="category-grid">
      {categories.map(([icon, name, count]) => (
        <a href="#products" className="category-card" key={name}>
          <div className="category-icon"><Icon name={icon} /></div>
          <strong>{name}</strong>
          <small>{count}</small>
        </a>
      ))}
    </div>
  );
}
