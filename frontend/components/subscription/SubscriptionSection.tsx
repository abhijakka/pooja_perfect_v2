import { Icon } from "../Icon";
import { SubscriptionModal } from "./SubscriptionModal";
import type { SubscriptionModalProps } from "./SubscriptionModal";

type SubscriptionSectionProps = {
  onPlanSelect: (plan: string) => void;
  onPayGoSelect: () => void;
  modalProps?: SubscriptionModalProps;
};

const planCards = [
  ["1_day", "ONE DAY", "1 Day Pack", "Choose one exact delivery date.", "49", "One delivery", "diya"],
  ["2_days", "TWO DAYS", "2 Days Pack", "Choose two different exact dates.", "98", "Two deliveries", "diya"],
  ["monthly_1_day", "MONTHLY", "1 Month · 1 Day", "Choose one weekday and repeat throughout one month.", "49", "1 recurring weekday", "lotus"],
  ["monthly_2_days", "MONTHLY", "1 Month · 2 Days", "Choose two weekdays and repeat throughout one month.", "98", "2 recurring weekdays", "lotus"],
  ["paygo", "FLEXIBLE", "Pay As You Go", "Search and select products with your own delivery pattern.", "Custom", "Build your own pack", "sparkle"],
] as const;

const packItems = [
  ["🍌", "Banana", "6 pieces"],
  ["🔴", "Kumkuma", "1 pack"],
  ["🟡", "Pasupu", "1 pack"],
  ["🥥", "Coconut", "1 piece"],
  ["🌸", "Flowers", "250 grams"],
] as const;

export function SubscriptionSection({ onPlanSelect, onPayGoSelect, modalProps }: SubscriptionSectionProps) {
  return (
    <section className="subscription" id="subscriptions">
      <div className="subscription-head"><div><span className="subscription-eyebrow">POOJAPOINT SUBSCRIPTIONS</span><h2>Your pooja, <span>your schedule.</span></h2><p className="subscription-intro">Choose a regular delivery plan or use Pay As You Go to select multiple products and your own delivery schedule.</p></div></div>
      <div className="pack-box"><div className="pack-title">Standard PoojaPoint Essentials Pack</div><div className="pack-grid">{packItems.map(([emoji, name, detail]) => <div className="pack-item" key={name}><span className="pack-emoji">{emoji}</span><div><strong>{name}</strong><small>{detail}</small></div></div>)}</div></div>
      <div className="plans">{planCards.map(([key, tag, name, description, price, included, icon]) => <article className={`plan ${key === "monthly_1_day" ? "featured" : ""}`} key={key}>{key === "monthly_1_day" && <div className="popular">★ MOST POPULAR</div>}<div className="plan-top"><div className="plan-icon"><Icon name={icon} /></div><span className="plan-tag">{tag}</span></div><h3>{name}</h3><p className="plan-desc">{description}</p><div className="price"><span>{price === "Custom" ? "" : "₹"}</span><strong>{price}</strong><small>{price === "Custom" ? "" : "/ pack"}</small></div><div className="included"><span>✓</span> {included}</div><ul className="features"><li>Fresh pooja essentials</li><li>Carefully packed</li><li>Flexible scheduling</li><li>Secure checkout</li></ul><button className={`plan-button ${key === "monthly_1_day" || key === "paygo" ? "primary" : ""}`} onClick={() => key === "paygo" ? onPayGoSelect() : onPlanSelect(key)}>{key === "paygo" ? "Customize Pack" : key.startsWith("monthly") ? "Subscribe Now" : `Choose ${key === "1_day" ? "1 Day" : "2 Days"}`}</button></article>)}</div>
      <p className="subscription-note">🌸 Fresh essentials · Carefully packed · Flexible schedules · Secure checkout</p>
      {modalProps && <SubscriptionModal {...modalProps} />}
    </section>
  );
}
