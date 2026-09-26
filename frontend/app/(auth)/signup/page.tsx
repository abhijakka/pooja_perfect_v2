"use client";

import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import { useFormik } from "formik";
import * as yup from "yup";
import { email, name, password, phone } from "../../../lib/validation";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Icon } from "../../../components/Icon";
import { PublicFooter } from "../../../components/layout/PublicFooter/PublicFooter";
import { PublicHeader } from "../../../components/layout/PublicHeader/PublicHeader";
import { useCart } from "../../../hooks/useCart";
import { useWishlist } from "../../../hooks/useWishlist";
import { useGoogleAuth } from "../../../hooks/useGoogleAuth";
import { products } from "../../(public)/storefront-data";
import { authApi } from "../../../services/api/auth.api";

type Fields = { firstName: string; lastName: string; email: string; phone: string; password: string; confirmPassword: string };

export default function SignupPage() {
	const router = useRouter();
	const { count: cartCount } = useCart();
	const { count: wishlistCount } = useWishlist();
	const [query, setQuery] = useState("");
	const [nav, setNav] = useState("profile");
	const [visible, setVisible] = useState({ password: false, confirmPassword: false });
	const [loading, setLoading] = useState(false);
	const [toast, setToast] = useState("");
	const suggestions = useMemo(() => query ? products.filter((product) => `${product.name} ${product.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : [], [query]);
	const formik = useFormik({
		initialValues: { firstName: "", lastName: "", email: "", phone: "", password: "", confirmPassword: "", terms: false },
		validationSchema: yup.object({
			firstName: name.required("Enter your first name"),
			lastName: name.required("Enter your last name"),
			email: email.required("Enter your email address"),
			phone: phone.required("Enter your mobile number"),
			password: password.required("Enter a password"),
			confirmPassword: yup.string().oneOf([yup.ref("password")], "Passwords do not match").required("Confirm your password"),
			terms: yup.boolean().oneOf([true], "Please accept the Terms & Conditions"),
		}),
		onSubmit: async (values) => {
			setLoading(true);
			try {
				await authApi.register({
					first_name: values.firstName,
					last_name: values.lastName,
					email: values.email,
					phone: values.phone,
					password: values.password,
					confirm_password: values.confirmPassword,
				});
				notify("Welcome to PoojaPoint");
				window.setTimeout(() => router.push("/login"), 700);
			} catch (error) {
				const message = error instanceof Error ? error.message : "Sign up failed";
				notify(message);
			} finally {
				setLoading(false);
			}
		},
	});
	const fields = formik.values;
	const terms = formik.values.terms;
	const submitted = formik.submitCount > 0;
	const strength = Math.min(4, Number(fields.password.length >= 8) + Number(/[a-z]/.test(fields.password)) + Number(/[A-Z]/.test(fields.password)) + Number(/[0-9!@#$%^&*]/.test(fields.password)));
	const update = (key: keyof Fields, value: string) => formik.setFieldValue(key, key === "phone" ? value.replace(/\D/g, "").slice(0, 10) : value);
	const invalid = (key: keyof Fields) => Boolean(formik.touched[key] && formik.errors[key]);
	const setTerms = (value: boolean) => formik.setFieldValue("terms", value);
	const notify = (message: string) => { setToast(message); window.setTimeout(() => setToast(""), 2500); };
	// Registering with Google authenticates immediately, so this page reuses the
	// same shared sign-in flow as /login and only owns its own copy and the
	// role-based landing page.
	const { isBusy: googleBusy, signInWithGoogle } = useGoogleAuth({ onError: notify });
	const continueWithGoogle = async () => {
		const me = await signInWithGoogle();
		if (!me) return;
		notify("Welcome to PoojaPoint");
		window.setTimeout(() => {
			if (me.role_name === "admin") router.push("/admin");
			else router.push("/");
		}, 700);
	};
	const submitSearch = (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); if (!query.trim()) notify("Type a product name"); };
	const submit = formik.handleSubmit;

	return <div className="signup-page">
		<PublicHeader query={query} suggestions={suggestions} cartCount={cartCount} wishlistCount={wishlistCount} onQueryChange={setQuery} onSearch={submitSearch} onProfile={() => notify("Already on the sign-up page")} onWishlist={() => router.push("/wishlist")} onCart={() => router.push("/cart")} />
		<main className="signup-main"><section className="signup-wrapper"><div className="signup-brand-panel"><div className="signup-brand-content"><div className="signup-brand-symbol"><Icon name="gift" /></div><h1>Welcome to <span>PoojaPoint</span></h1><p>Create your account and enjoy a smoother, more personal shopping experience for all your pooja essentials.</p><div className="signup-benefits"><div><span><Icon name="user" /></span>Personalized shopping</div><div><span><Icon name="gift" /></span>Save your favourite products</div><div><span><Icon name="shield" /></span>Safe & secure account</div><div><span><Icon name="lock" /></span>Easy order tracking</div></div></div></div><div className="signup-form-panel"><div className="signup-form-header"><h2>Create your account</h2><p>It&apos;s quick, simple and completely free.</p></div><form onSubmit={submit} noValidate><div className="signup-field-row">{([["firstName", "First name", "Your first name", "user"], ["lastName", "Last name", "Your last name", "user"]] as const).map(([key, label, placeholder, icon]) => <div className={`signup-field ${invalid(key) ? "invalid" : ""}`} key={key}><label htmlFor={key}>{label}</label><div className="signup-input-wrapper"><Icon name={icon} /><input id={key} value={fields[key]} onChange={(event) => update(key, event.target.value)} placeholder={placeholder} autoComplete={key === "firstName" ? "given-name" : "family-name"} /><small>Enter your {key === "firstName" ? "first" : "last"} name.</small></div></div>)}</div>{([ ["email", "Email address", "you@example.com", "mail", "email"], ["phone", "Mobile number", "10-digit mobile number", "phone", "tel"] ] as const).map(([key, label, placeholder, icon, type]) => <div className={`signup-field ${invalid(key) ? "invalid" : ""}`} key={key}><label htmlFor={key}>{label}</label><div className="signup-input-wrapper"><Icon name={icon} /><input id={key} type={type} value={fields[key]} onChange={(event) => update(key, event.target.value)} placeholder={placeholder} inputMode={key === "phone" ? "numeric" : undefined} autoComplete={key} /><small>{key === "email" ? "Enter a valid email address." : "Enter a valid 10-digit mobile number."}</small></div></div>)}{([ ["password", "Password", "Create a strong password"], ["confirmPassword", "Confirm password", "Enter password again"] ] as const).map(([key, label, placeholder]) => <div className={`signup-field ${invalid(key) ? "invalid" : ""}`} key={key}><label htmlFor={key}>{label}</label><div className="signup-input-wrapper"><Icon name="lock" /><input id={key} type={visible[key] ? "text" : "password"} value={fields[key]} onChange={(event) => update(key, event.target.value)} placeholder={placeholder} autoComplete="new-password" /><button type="button" onClick={() => setVisible((current) => ({ ...current, [key]: !current[key] }))} aria-label={visible[key] ? "Hide password" : "Show password"}><Icon name={visible[key] ? "eye-off" : "eye"} /></button></div>{key === "password" && fields.password && <div className="signup-strength"><div>{[1, 2, 3, 4].map((bar) => <span className={bar <= strength ? `level-${strength}` : ""} key={bar} />)}</div><small>{strength <= 1 ? "Weak password" : strength === 2 ? "Fair password" : strength === 3 ? "Good password" : "Strong password"}</small></div>}<small className="signup-error">{key === "password" ? "Password must contain at least 8 characters." : "Passwords do not match."}</small></div>)}<div className={`signup-terms ${submitted && !terms ? "invalid" : ""}`}><input id="terms" type="checkbox" checked={terms} onChange={(event) => setTerms(event.target.checked)} /><label htmlFor="terms">I agree to the <Link href="/terms">Terms &amp; Conditions</Link> and <Link href="/privacy">Privacy Policy</Link>.</label></div><button className="signup-submit" type="submit" disabled={loading || googleBusy}>{loading ? <span className="signup-spinner" /> : <>Create Account <Icon name="arrow-right" /></>}</button><div className="signup-divider"><span>OR</span></div><button className="signup-google" type="button" onClick={continueWithGoogle} disabled={loading || googleBusy} aria-busy={googleBusy}><strong>G</strong> Continue with Google</button><p className="signup-login">Already have an account? <Link href="/login">Sign in</Link></p><div className="signup-security"><Icon name="shield" /> Your information is encrypted and securely protected.</div></form></div></section></main>
		<PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={cartCount} onNavChange={setNav} onWishlist={() => router.push("/wishlist")} onProfile={() => notify("Already on the sign-up page")} />
		{toast && <div className="toast show">{toast}</div>}
	</div>;
}
