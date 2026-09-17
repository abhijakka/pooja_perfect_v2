import { Icon } from "../Icon";

type TrustGridProps = {
  items: readonly (readonly [string, string, string])[];
};

export function TrustGrid({ items }: TrustGridProps) {
  return (
    <div className="trust-grid">
      {items.map(([icon, title, description]) => (
        <div className="trust-card" key={title}>
          <div className="trust-icon"><Icon name={icon} /></div>
          <strong>{title}</strong>
          <span>{description}</span>
        </div>
      ))}
    </div>
  );
}
