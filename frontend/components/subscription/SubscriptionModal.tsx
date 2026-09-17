import { Icon } from "../Icon";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { DatePicker } from "./DatePicker";

type Plan = {
  name: string;
  price: number;
  kind: "date" | "weekday";
  count: number;
};
type PlanKey = "1_day" | "2_days" | "monthly_1_day" | "monthly_2_days";
type Product = {
  id: string;
  name: string;
  category: string;
  price: number;
  image?: string;
};
type SelectedProduct = Product & { quantity: number };

export type SubscriptionModalProps = {
  open: boolean;
  payGo: boolean;
  plan: PlanKey | null;
  plans: Record<PlanKey, Plan>;
  products: Product[];
  selectedProducts: SelectedProduct[];
  payGoQuery: string;
  dates: string[];
  weekdays: string[];
  deliveryTime: string;
  immediateAvailable: boolean;
  valid: boolean;
  onClose: () => void;
  onProductSearch: (value: string) => void;
  onAddProduct: (product: Product) => void;
  onDecreaseProduct: (id: string) => void;
  onRemoveProduct: (id: string) => void;
  onClearProducts: () => void;
  onPlanSelect: (plan: PlanKey) => void;
  onDateChange: (index: number, value: string) => void;
  onWeekdayChange: (index: number, value: string) => void;
  onDeliveryTime: (value: string) => void;
  onConfirm: () => void;
};

const deliveryTimes = [
  ["immediate", "Immediately", "Available now · 6:00 AM - 6:00 PM", "⚡"],
  ["06:00-09:00", "Early Morning", "6:00 AM - 9:00 AM", "🌅"],
  ["09:00-12:00", "Morning", "9:00 AM - 12:00 PM", "☀️"],
  ["12:00-15:00", "Afternoon", "12:00 PM - 3:00 PM", "🌤️"],
  ["15:00-18:00", "Evening", "3:00 PM - 6:00 PM", "🌇"],
] as const;

const weekdays = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
];
const money = (value: number) => `₹${value.toLocaleString("en-IN")}`;
const today = () => new Date().toISOString().slice(0, 10);

function countWeekdaysInMonth(weekdayIndex: number): number {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  let count = 0;
  for (let day = 1; day <= daysInMonth; day++) {
    if (new Date(year, month, day).getDay() === weekdayIndex) {
      count++;
    }
  }
  return count;
}

function getMultiplier(plan: PlanKey | null, selectedWeekdays: string[]): number {
  if (!plan) return 1;
  if (plan === "1_day") return 1;
  if (plan === "2_days") return 2;
  if (plan === "monthly_1_day") {
    const weekday = selectedWeekdays[0];
    return weekday ? countWeekdaysInMonth(Number(weekday)) : 1;
  }
  if (plan === "monthly_2_days") {
    const w1 = selectedWeekdays[0];
    const w2 = selectedWeekdays[1];
    const count1 = w1 ? countWeekdaysInMonth(Number(w1)) : 0;
    const count2 = w2 ? countWeekdaysInMonth(Number(w2)) : 0;
    return count1 + count2;
  }
  return 1;
}

function WeekdaySelect({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  const [open, setOpen] = useState(false);
  const selected = value ? weekdays[Number(value)] : "Select weekday";

  return (
    <div className="weekday-picker">
      <button
        type="button"
        className={`weekday-select ${open ? "open" : ""}`}
        onClick={() => setOpen((current) => !current)}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        {selected}
        {value && <span className="date-selection-check" aria-hidden="true">✓</span>}
      </button>
      {open && (
        <div className="weekday-options" role="listbox">
          <button type="button" className="weekday-option" onClick={() => { onChange(""); setOpen(false); }}>
            Select weekday
          </button>
          {weekdays.map((day, index) => (
            <button
              type="button"
              className={`weekday-option ${value === String(index) ? "selected" : ""}`}
              onClick={() => { onChange(String(index)); setOpen(false); }}
              role="option"
              aria-selected={value === String(index)}
              key={day}
            >
              {day}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export function SubscriptionModal({
  open,
  payGo,
  plan,
  plans,
  products,
  selectedProducts,
  payGoQuery,
  dates,
  weekdays: selectedWeekdays,
  deliveryTime,
  immediateAvailable,
  valid,
  onClose,
  onProductSearch,
  onAddProduct,
  onDecreaseProduct,
  onRemoveProduct,
  onClearProducts,
  onPlanSelect,
  onDateChange,
  onWeekdayChange,
  onDeliveryTime,
  onConfirm,
}: SubscriptionModalProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!open || !mounted) return null;
  const activePlan = plan ? plans[plan] : null;
  const multiplier = getMultiplier(plan, selectedWeekdays);
  const baseTotal = selectedProducts.reduce(
    (sum, product) => sum + product.price * product.quantity,
    0,
  );
  const total = baseTotal * multiplier;
  const results = products.filter((product) =>
    `${product.name} ${product.category}`
      .toLowerCase()
      .includes(payGoQuery.toLowerCase()),
  );

  return createPortal(
    (
    <div
      className="modal-overlay show"
      id="subscriptionModal"
      onMouseDown={(event) => event.target === event.currentTarget && onClose()}
    >
      <div className="modal">
        <button className="modal-close" onClick={onClose} aria-label="Close">
          ×
        </button>
        <div className="modal-icon">
          <Icon name="sparkle" />
        </div>
        <span className="modal-label">CUSTOMIZE YOUR DELIVERY</span>
        <h2>{payGo ? "Build your own pack" : activePlan?.name}</h2>
        <p className="modal-subtitle">
          {payGo
            ? "Search products, select multiple items and choose your delivery schedule."
            : "Select your preferred delivery schedule."}
        </p>
        {payGo && (
          <div className="paygo-box">
            <div className="paygo-title">1. Search & choose products</div>
            <p className="paygo-help">
              Search any product and add multiple products to your custom pack.
            </p>
            <div className="paygo-search">
              <Icon name="search" />
              <input
                value={payGoQuery}
                onChange={(event) => onProductSearch(event.target.value)}
                placeholder="Search diya, flower, coconut..."
              />
              <button type="button" onClick={() => onProductSearch("")}>
                ×
              </button>
            </div>
            <div className="paygo-product-results">
              {results.map((product) => {
                const selected = selectedProducts.some((item) => item.id === product.id);

                return (
                <div className={`paygo-product-card ${selected ? "selected" : ""}`} key={product.id}>
                  {product.image ? (
                    <img src={product.image} alt={product.name} />
                  ) : (
                    <div className="paygo-product-image">
                      <Icon name="flower" />
                    </div>
                  )}
                  <div className="paygo-product-info">
                    <strong>{product.name}</strong>
                    <small>{product.category}</small>
                    <b>{money(product.price)}</b>
                  </div>
                  <button
                    type="button"
                    className={`paygo-add ${selected ? "selected" : ""}`}
                    aria-label={selected ? `Remove ${product.name}` : `Add ${product.name}`}
                    onClick={() => selected ? onRemoveProduct(product.id) : onAddProduct(product)}
                  >
                    {selected ? "−" : "+"}
                  </button>
                </div>
                );
              })}
            </div>
            <div className="selected-products-section">
              <div className="selected-products-head">
                <strong>
                  Selected products{" "}
                  <small>
                    {selectedProducts.reduce(
                      (sum, product) => sum + product.quantity,
                      0,
                    )}{" "}
                    items
                  </small>
                </strong>
                <button className="clear-products" onClick={onClearProducts}>
                  Clear all
                </button>
              </div>
              {selectedProducts.length === 0 ? (
                <div className="no-products">
                  🛍️<p>No products selected yet</p>
                  <small>Search above and tap +</small>
                </div>
              ) : (
                selectedProducts.map((product) => (
                  <div className="selected-paygo-item" key={product.id}>
                    <div className="selected-paygo-info">
                      <strong>{product.name}</strong>
                      <small>
                        {money(product.price)} × {product.quantity}
                      </small>
                    </div>
                    <div className="quantity-control">
                      <button
                        onClick={() =>
                          product.quantity > 1
                            ? onDecreaseProduct(product.id)
                            : onRemoveProduct(product.id)
                        }
                      >
                        -
                      </button>
                      <span>{product.quantity}</span>
                      <button onClick={() => onAddProduct(product)}>+</button>
                    </div>
                  </div>
                ))
              )}
            </div>
            <div className="paygo-title paygo-plan-title">
              2. Choose delivery plan
            </div>
          </div>
        )}
        {payGo && (
          <div className="paygo-plans">
            {(Object.keys(plans) as PlanKey[]).map((key) => (
              <button
                className={`paygo-option ${plan === key ? "active" : ""}`}
                onClick={() => onPlanSelect(key)}
                key={key}
              >
                <span className="paygo-check" aria-hidden="true">✓</span>
                <strong>{plans[key].name}</strong>
                <small>
                  {plans[key].kind === "date"
                    ? `Choose ${plans[key].count} exact date${plans[key].count > 1 ? "s" : ""}`
                    : `Choose ${plans[key].count} weekday${plans[key].count > 1 ? "s" : ""}`}
                </small>
              </button>
            ))}
          </div>
        )}
        <div className="selected-plan">
          <div>
            <small>SELECTED PLAN</small>
            <strong>{activePlan?.name ?? "Choose a delivery plan"}</strong>
          </div>
          <b>
            {payGo && plan
              ? money(total)
              : activePlan
                ? money(activePlan.price)
                : "₹-"}
          </b>
        </div>
        {activePlan && (
          <div className="date-section">
            <label>
              {activePlan.kind === "date"
                ? "Select your delivery date"
                : "Choose your delivery weekday"}
            </label>
            <div className="date-fields">
              {Array.from({ length: activePlan.count }, (_, index) =>
                activePlan.kind === "date" ? (
                  <DatePicker
                    min={today()}
                    value={dates[index] ?? ""}
                    onChange={(value) => onDateChange(index, value)}
                    key={index}
                  />
                ) : (
                  <WeekdaySelect
                    value={selectedWeekdays[index] ?? ""}
                    onChange={(value) => onWeekdayChange(index, value)}
                    key={index}
                  />
                ),
              )}
            </div>
            <div className="date-preview">
              {(activePlan.kind === "date" ? dates : selectedWeekdays).length
                ? (activePlan.kind === "date" ? dates : selectedWeekdays).map(
                    (value) => (
                      <span className="date-chip" key={value}>
                        {activePlan.kind === "date"
                          ? new Date(`${value}T00:00:00`).toLocaleDateString(
                              "en-IN",
                              {
                                day: "numeric",
                                month: "short",
                                year: "numeric",
                              },
                            )
                          : weekdays[Number(value)]}
                      </span>
                    ),
                  )
                : "Choose your delivery schedule."}
            </div>
          </div>
        )}
        <div className="delivery-time-section">
          <div className="delivery-time-head">
            <label className="delivery-time-title">
              When should we deliver?
            </label>
            <span className="delivery-time-required">REQUIRED</span>
          </div>
          <p className="delivery-time-help">
            Choose Immediate delivery or a preferred time window. Delivery
            service is open daily from 6:00 AM to 6:00 PM.
          </p>
          <div className="delivery-time-options">
            {deliveryTimes.map(([value, label, description, icon]) => (
              <button
                className={`delivery-time-option ${deliveryTime === value ? "active" : ""}`}
                disabled={value === "immediate" && !immediateAvailable}
                onClick={() => onDeliveryTime(value)}
                key={value}
              >
                <span className="delivery-time-icon">{icon}</span>
                <strong>{label}</strong>
                <small>
                  {value === "immediate" && !immediateAvailable
                    ? "Available daily from 6:00 AM - 6:00 PM"
                    : description}
                </small>
                <span className="delivery-time-check" aria-hidden="true">✓</span>
              </button>
            ))}
          </div>
          <div className="selected-delivery-time">
            {deliveryTime
              ? deliveryTimes.find(([value]) => value === deliveryTime)?.[2]
              : "Please select a delivery time."}
          </div>
        </div>
        <button
          className="confirm"
          id="confirmSubscription"
          disabled={!valid}
          onClick={onConfirm}
        >
          Add to cart
        </button>
      </div>
    </div>
    ),
    document.body,
  );
}
