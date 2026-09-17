"use client";

import { useEffect, useRef, useState } from "react";
import type { ClipboardEvent, FormEvent, KeyboardEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Icon } from "../../../components/Icon";
import { PublicFooter } from "../../../components/layout/PublicFooter/PublicFooter";
import { PublicHeader } from "../../../components/layout/PublicHeader/PublicHeader";
import { useCart } from "../../../hooks/useCart";
import { useWishlist } from "../../../hooks/useWishlist";
import { products } from "../../(public)/storefront-data";

export default function TwoFactorPage() {
	const router = useRouter();
	const { count: cartCount } = useCart();
	const { count: wishlistCount } = useWishlist();
	const [query, setQuery] = useState("");
	const [nav, setNav] = useState("profile");
	const [digits, setDigits] = useState(["", "", "", "", "", ""]);
	const [trustDevice, setTrustDevice] = useState(false);
	const [error, setError] = useState("");
	const [verifying, setVerifying] = useState(false);
	const [backupOpen, setBackupOpen] = useState(false);
	const [backupCode, setBackupCode] = useState("");
	const [backupLoading, setBackupLoading] = useState(false);
	const [toast, setToast] = useState("");
	const inputRefs = useRef<Array<HTMLInputElement | null>>([]);
	const suggestions = query ? products.filter((product) => `${product.name} ${product.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : [];

	useEffect(() => { inputRefs.current[0]?.focus(); }, []);
	const notify = (message: string) => { setToast(message); window.setTimeout(() => setToast(""), 2500); };
	const updateDigit = (index: number, value: string) => {
		const digit = value.replace(/\D/g, "").slice(-1);
		setDigits((current) => current.map((item, position) => position === index ? digit : item));
		setError("");
		if (digit && index < 5) inputRefs.current[index + 1]?.focus();
	};
	const handleKeyDown = (index: number, event: KeyboardEvent<HTMLInputElement>) => {
		if (event.key === "Backspace" && !digits[index] && index > 0) inputRefs.current[index - 1]?.focus();
		if (event.key === "ArrowLeft" && index > 0) inputRefs.current[index - 1]?.focus();
		if (event.key === "ArrowRight" && index < 5) inputRefs.current[index + 1]?.focus();
	};
	const handlePaste = (event: ClipboardEvent<HTMLInputElement>) => {
		event.preventDefault();
		const pasted = event.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6).split("");
		setDigits((current) => current.map((_, index) => pasted[index] ?? ""));
		setError("");
		inputRefs.current[Math.min(pasted.length, 5)]?.focus();
	};
	const verify = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		const code = digits.join("");
		if (code.length !== 6) { setError("Enter the complete 6-digit security code."); inputRefs.current[code.length]?.focus(); return; }
		setVerifying(true);
		window.setTimeout(() => {
			if (code !== "123456") { setError("Incorrect security code. Try again."); setVerifying(false); inputRefs.current[0]?.focus(); return; }
			notify("Two-factor authentication successful");
			window.setTimeout(() => router.push("/my-account"), 800);
		}, 700);
	};
	const verifyBackup = () => {
		if (!backupCode.trim()) return notify("Enter your backup code");
		setBackupLoading(true);
		window.setTimeout(() => {
			if (backupCode.trim().toUpperCase() !== "POJA-2026") { notify("Invalid backup code"); setBackupLoading(false); return; }
			notify("Backup code accepted");
			window.setTimeout(() => router.push("/my-account"), 800);
		}, 700);
	};

	return <div className="two-factor-page"><PublicHeader query={query} suggestions={suggestions} cartCount={cartCount} wishlistCount={wishlistCount} onQueryChange={setQuery} onSearch={(event) => { event.preventDefault(); if (!query.trim()) notify("Type a product name"); }} onProfile={() => notify("Already on the verification page")} onWishlist={() => router.push("/wishlist")} onCart={() => router.push("/cart")} /><main className="two-factor-main"><section className="two-factor-card"><div className="two-factor-icon"><Icon name="shield" /></div><h1>Two-factor authentication</h1><p className="two-factor-subtitle">Enter the 6-digit security code from your authenticator app to complete your sign in.</p><div className="authenticator-box"><div><Icon name="lock" /></div><p><strong>Authenticator app</strong><span>Open your authenticator app and enter the current code.</span></p></div><form onSubmit={verify}><div className="two-factor-inputs">{digits.map((digit, index) => <input className={`two-factor-input ${error ? "error" : ""}`} key={index} ref={(element) => { inputRefs.current[index] = element; }} value={digit} onChange={(event) => updateDigit(index, event.target.value)} onKeyDown={(event) => handleKeyDown(index, event)} onPaste={handlePaste} inputMode="numeric" maxLength={1} autoComplete={index === 0 ? "one-time-code" : "off"} aria-label={`Security code digit ${index + 1}`} />)}</div><div className="two-factor-error" aria-live="polite">{error}</div><label className="trust-device"><input type="checkbox" checked={trustDevice} onChange={(event) => setTrustDevice(event.target.checked)} /><span><strong>Trust this device</strong>Don&apos;t ask for a verification code on this device for the next 30 days.</span></label><button className="two-factor-verify" type="submit" disabled={verifying}>{verifying ? <span className="two-factor-spinner" /> : <>Verify &amp; Continue <Icon name="arrow-right" /></>}</button></form><div className="backup-section"><p>Can&apos;t access your authenticator?</p><button type="button" onClick={() => setBackupOpen((value) => !value)}>{backupOpen ? "Hide backup code" : "Use a backup code"}</button>{backupOpen && <div className="backup-form"><label htmlFor="backup-code">Backup code</label><input id="backup-code" value={backupCode} onChange={(event) => setBackupCode(event.target.value)} placeholder="XXXX-XXXX" autoComplete="off" maxLength={20} /><button type="button" onClick={verifyBackup} disabled={backupLoading}>{backupLoading ? "Verifying..." : "Verify backup code"}</button></div>}</div><div className="two-factor-security"><Icon name="lock" /> Your verification code is private. Never share it with anyone.</div></section></main><PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={cartCount} onNavChange={setNav} onWishlist={() => router.push("/wishlist")} onProfile={() => notify("Already on the verification page")} />{toast && <div className="toast show">{toast}</div>}</div>;
}
