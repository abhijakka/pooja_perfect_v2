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

export default function OtpPage() {
	const router = useRouter();
	const { count: cartCount } = useCart();
	const { count: wishlistCount } = useWishlist();
	const [query, setQuery] = useState("");
	const [nav, setNav] = useState("profile");
	const [digits, setDigits] = useState(["", "", "", "", "", ""]);
	const [error, setError] = useState("");
	const [verifying, setVerifying] = useState(false);
	const [resendSeconds, setResendSeconds] = useState(30);
	const [toast, setToast] = useState("");
	const inputRefs = useRef<Array<HTMLInputElement | null>>([]);
	const suggestions = query ? products.filter((product) => `${product.name} ${product.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : [];

	useEffect(() => {
		if (!resendSeconds) return;
		const timer = window.setInterval(() => setResendSeconds((value) => Math.max(0, value - 1)), 1000);
		return () => window.clearInterval(timer);
	}, [resendSeconds]);
	const notify = (message: string) => { setToast(message); window.setTimeout(() => setToast(""), 2500); };
	const clearError = () => setError("");
	const updateDigit = (index: number, value: string) => {
		const digit = value.replace(/\D/g, "").slice(-1);
		setDigits((current) => current.map((item, position) => position === index ? digit : item));
		clearError();
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
		clearError();
		inputRefs.current[Math.min(pasted.length, 5)]?.focus();
	};
	const submit = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		const otp = digits.join("");
		if (otp.length !== 6) { setError("Please enter the complete 6-digit OTP."); inputRefs.current[otp.length]?.focus(); return; }
		setVerifying(true);
		window.setTimeout(() => {
			if (otp !== "123456") { setError("The OTP is incorrect. Please try again."); setVerifying(false); inputRefs.current[0]?.focus(); return; }
			notify("Account verified successfully");
			window.setTimeout(() => router.push("/my-account"), 800);
		}, 700);
	};
	const resend = () => {
		if (resendSeconds) return;
		setDigits(["", "", "", "", "", ""]); setError(""); setResendSeconds(30); notify("A new OTP has been sent"); inputRefs.current[0]?.focus();
	};

	return <div className="otp-page"><PublicHeader query={query} suggestions={suggestions} cartCount={cartCount} wishlistCount={wishlistCount} onQueryChange={setQuery} onSearch={(event) => { event.preventDefault(); if (!query.trim()) notify("Type a product name"); }} onProfile={() => notify("Already on the verification page")} onWishlist={() => router.push("/wishlist")} onCart={() => router.push("/cart")} /><main className="otp-main"><section className="otp-card"><div className="otp-icon"><Icon name="lock" /></div><h1>Verify your account</h1><p className="otp-subtitle">We&apos;ve sent a 6-digit verification code to the contact below.</p><div className="otp-contact"><Icon name="mail" /> a******@example.com</div><Link href="/login" className="otp-change-contact">Change email or mobile</Link><form onSubmit={submit}><div className="otp-inputs">{digits.map((digit, index) => <input className={`otp-input ${error ? "error" : ""}`} key={index} ref={(element) => { inputRefs.current[index] = element; }} value={digit} onChange={(event) => updateDigit(index, event.target.value)} onKeyDown={(event) => handleKeyDown(index, event)} onPaste={handlePaste} inputMode="numeric" maxLength={1} autoComplete={index === 0 ? "one-time-code" : "off"} aria-label={`OTP digit ${index + 1}`} />)}</div><div className="otp-error" aria-live="polite">{error}</div><button className="otp-verify" type="submit" disabled={verifying}>{verifying ? <span className="otp-spinner" /> : <>Verify &amp; Continue <Icon name="arrow-right" /></>}</button></form><div className="otp-resend">Didn&apos;t receive the code?<button type="button" onClick={resend} disabled={Boolean(resendSeconds)}>Resend OTP <span>{resendSeconds ? `${resendSeconds}s` : ""}</span></button></div><div className="otp-security"><Icon name="shield" /> Never share your OTP with anyone. PoojaPoint will never ask for it.</div></section></main><PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={cartCount} onNavChange={setNav} onWishlist={() => router.push("/wishlist")} onProfile={() => notify("Already on the verification page")} />{toast && <div className="toast show">{toast}</div>}</div>;
}
