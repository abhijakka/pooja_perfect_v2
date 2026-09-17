import { useEffect } from "react";
import { Icon } from "../Icon";

type RemoveConfirmationModalProps = {
  open: boolean;
  title?: string;
  message?: string;
  confirmLabel?: string;
  onCancel: () => void;
  onConfirm: () => void;
};

export function RemoveConfirmationModal({
  open,
  title = "Remove Item?",
  message = "Are you sure you want to remove this item from your cart?",
  confirmLabel = "Remove",
  onCancel,
  onConfirm,
}: RemoveConfirmationModalProps) {
  useEffect(() => {
    if (!open) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onCancel();
    };

    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = "";
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [onCancel, open]);

  if (!open) return null;

  return (
    <div
      className="modal-overlay show"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onCancel();
      }}
    >
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="remove-item-title" style={{ maxWidth: 380, textAlign: "center" }}>
        <div className="modal-icon" style={{ margin: "0 auto 15px" }}>
          <Icon name="trash" />
        </div>
        <h2 id="remove-item-title">{title}</h2>
        <p className="modal-subtitle">{message}</p>
        <div style={{ display: "flex", gap: 9, marginTop: 22 }}>
          <button type="button" className="plan-button" style={{ flex: 1, marginTop: 0 }} onClick={onCancel}>
            Cancel
          </button>
          <button type="button" className="plan-button primary" style={{ flex: 1, marginTop: 0 }} onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}