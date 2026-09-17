"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { useFormik } from "formik";
import * as yup from "yup";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Icon } from "../../../components/Icon";
import { PublicHeader } from "../../../components/layout/PublicHeader/PublicHeader";
import { PublicFooter } from "../../../components/layout/PublicFooter/PublicFooter";
import { useCart } from "../../../hooks/useCart";
import { useWishlist } from "../../../hooks/useWishlist";
import { products } from "../../(public)/storefront-data";
import { authApi } from "../../../services/api/auth.api";
import { useAppDispatch } from "../../../store/hooks";
import { setUser } from "../../../store/slices/authSlice";

export default function LoginPage() {
	const router = useRouter();
	const dispatch = useAppDispatch();
	const { count: cartCount } = useCart();
	const { count: wishlistCount } = useWishlist();
	const [query, setQuery] = useState("");
	const [nav, setNav] = useState("profile");
	const [showPassword, setShowPassword] = useState(false);
	const [loading, setLoading] = useState(false);
	const [toast, setToast] = useState("");
	const suggestions = query ? products.filter((product) => `${product.name} ${product.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : [];

	const notify = (message: string) => {
		setToast(message);
		window.setTimeout(() => setToast(""), 2500);
	};
	const formik = useFormik({
		initialValues: { identifier: "", password: "", remember: false },
		validationSchema: yup.object({
			identifier: yup.string().required("Enter your email or mobile number"),
			password: yup.string().required("Enter your password"),
			remember: yup.boolean(),
		}),
		onSubmit: async (values) => {
			setLoading(true);
			try {
				await authApi.login({
					identifier: values.identifier,
					password: values.password,
					remember: values.remember,
				});
				const me = await authApi.me();
				dispatch(
					setUser({
						id: me.id,
						name: `${me.first_name} ${me.last_name}`.trim(),
						email: me.email,
						role_name: me.role_name,
					}),
				);
				notify("Welcome back to PoojaPoint");
				window.setTimeout(() => {
					if (me.role_name === "admin") router.push("/admin");
					else router.push("/");
				}, 700);
			} catch (error) {
				const message = error instanceof Error ? error.message : "Login failed";
				notify(message);
			} finally {
				setLoading(false);
			}
		},
	});

	const submitSearch = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		if (!query.trim()) notify("Type a product name");
	};
	return <div className="login-page">
		<PublicHeader query={query} suggestions={suggestions} cartCount={cartCount} wishlistCount={wishlistCount} onQueryChange={setQuery} onSearch={submitSearch} onProfile={() => notify("Already on the sign-in page")} onWishlist={() => router.push("/wishlist")} onCart={() => router.push("/cart")} />
		<main className="login-main"><section className="login-wrapper">
			<div className="login-brand-panel"><div className="login-brand-content"><div className="login-brand-symbol"><Icon name="gift" /></div><h1>Welcome back to <span>PoojaPoint</span></h1><p>Sign in to access your orders, wishlist, saved addresses and personalized shopping experience.</p><div className="login-benefits"><div><span><Icon name="user" /></span>Personalized account</div><div><span><Icon name="gift" /></span>Your saved wishlist</div><div><span><Icon name="shield" /></span>Secure sign in</div><div><span><Icon name="lock" /></span>Easy order tracking</div></div></div></div>
			<div className="login-form-panel"><div className="login-form-header"><h2>Sign in</h2><p>Enter your details to continue.</p></div><form onSubmit={formik.handleSubmit} noValidate>
				<div className={`login-field ${formik.touched.identifier && formik.errors.identifier ? "invalid" : ""}`}><label htmlFor="identifier">Email or mobile number</label><div className="login-input-wrapper"><Icon name="user" /><input id="identifier" {...formik.getFieldProps("identifier")} placeholder="Email or 10-digit mobile" autoComplete="username" maxLength={254} autoFocus /></div><small>{formik.touched.identifier && formik.errors.identifier ? formik.errors.identifier : "Enter your email or mobile number."}</small></div>
				<div className={`login-field ${formik.touched.password && formik.errors.password ? "invalid" : ""}`}><label htmlFor="password">Password</label><div className="login-input-wrapper"><Icon name="lock" /><input id="password" type={showPassword ? "text" : "password"} {...formik.getFieldProps("password")} placeholder="Enter your password" autoComplete="current-password" /><button type="button" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? "Hide password" : "Show password"}><Icon name={showPassword ? "eye-off" : "eye"} /></button></div><small>{formik.touched.password && formik.errors.password ? formik.errors.password : "Enter your password."}</small></div>
				<div className="login-options"><label><input type="checkbox" name="remember" checked={formik.values.remember} onChange={formik.handleChange} /> Remember me</label><Link href="/forgot-password">Forgot password?</Link></div>
				<button className="login-submit" type="submit" disabled={loading}>{loading ? <span className="login-spinner" /> : <>Sign In <Icon name="arrow-right" /></>}</button><div className="login-divider"><span>OR</span></div><button className="login-google" type="button" onClick={() => notify("Google sign in is ready to connect")}><strong>G</strong> Continue with Google</button><p className="login-signup">Don't have an account? <Link href="/signup">Create account</Link></p><div className="login-security"><Icon name="shield" /> Secure login · Your information is protected.</div>
			</form></div>
		</section></main>
		<PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={cartCount} onNavChange={setNav} onWishlist={() => router.push("/wishlist")} onProfile={() => notify("Already on the sign-in page")} />
		{toast && <div className="toast show">{toast}</div>}
	</div>;
}
