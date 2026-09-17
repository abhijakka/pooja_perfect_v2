"use client";

import { useEffect, useState } from "react";

export function PoojaPointLoader() {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = window.setTimeout(() => setVisible(false), 1200);
    return () => window.clearTimeout(timer);
  }, []);

  if (!visible) return null;

  return (
    <div className="pp-loader" role="status" aria-live="polite" aria-label="Preparing your sacred space">
      <div className="pp-loader-content">
        <div className="pp-loader-logo">
          Pooja<span>Point</span>
        </div>
        <div className="pp-loader-symbol" aria-hidden="true">
          <div className="pp-loader-ring" />
          <span>✦</span>
        </div>
        <div className="pp-loader-text">Preparing your sacred space</div>
        <div className="pp-loader-track" aria-hidden="true">
          <span />
        </div>
      </div>
    </div>
  );
}
