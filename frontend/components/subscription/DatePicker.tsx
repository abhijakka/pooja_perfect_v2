import { useState } from "react";

type DatePickerProps = {
  value: string;
  min: string;
  onChange: (value: string) => void;
};

const monthFormatter = new Intl.DateTimeFormat("en-IN", { month: "long", year: "numeric" });
const dayFormatter = new Intl.DateTimeFormat("en-CA", { day: "2-digit" });

function toDate(value: string) {
  const [year, month, day] = value.split("-").map(Number);
  return year && month && day ? new Date(year, month - 1, day) : new Date();
}

function toIso(date: Date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

export function DatePicker({ value, min, onChange }: DatePickerProps) {
  const [open, setOpen] = useState(false);
  const [month, setMonth] = useState(() => {
    const date = toDate(value || min);
    return new Date(date.getFullYear(), date.getMonth(), 1);
  });
  const selected = value ? toDate(value) : null;
  const minimum = toDate(min);
  const firstDay = new Date(month.getFullYear(), month.getMonth(), 1).getDay();
  const daysInMonth = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate();
  const days = Array.from({ length: firstDay + daysInMonth }, (_, index) => index < firstDay ? null : index - firstDay + 1);

  return (
    <div className="date-picker">
      <button type="button" className={`date-picker-trigger ${open ? "open" : ""} ${selected ? "has-selection" : ""}`} onClick={() => setOpen((current) => !current)} aria-haspopup="dialog" aria-expanded={open}>
        {selected ? selected.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }) : "Select date"}
        {selected && <span className="date-selection-check" aria-hidden="true">✓</span>}
      </button>
      {open && (
        <div className="date-picker-popover" role="dialog" aria-label="Choose delivery date">
          <div className="date-picker-header">
            <strong>{monthFormatter.format(month)}</strong>
            <div>
              <button type="button" onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() - 1, 1))} aria-label="Previous month">↑</button>
              <button type="button" onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() + 1, 1))} aria-label="Next month">↓</button>
            </div>
          </div>
          <div className="date-picker-weekdays">{["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"].map((day) => <span key={day}>{day}</span>)}</div>
          <div className="date-picker-days">
            {days.map((day, index) => {
              if (!day) return <span className="date-picker-empty" key={`empty-${index}`} />;
              const date = new Date(month.getFullYear(), month.getMonth(), day);
              const iso = toIso(date);
              const disabled = date < minimum;
              return <button type="button" className={`date-picker-day ${value === iso ? "selected" : ""}`} disabled={disabled} onClick={() => { onChange(iso); setOpen(false); }} key={iso}>{day}</button>;
            })}
          </div>
          <div className="date-picker-footer"><button type="button" onClick={() => { onChange(""); setOpen(false); }}>Clear</button><button type="button" onClick={() => { onChange(min); setMonth(new Date(minimum.getFullYear(), minimum.getMonth(), 1)); setOpen(false); }}>Today</button></div>
        </div>
      )}
    </div>
  );
}
