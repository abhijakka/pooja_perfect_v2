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

export default function ForgotPasswordPage() {
  const router = useRouter();
  const { count: cartCount } = useCart();
  const { count: wishlistCount } = useWishlist();
  const [query, setQuery] = useState("");
  const [nav, setNav] = useState("profile");
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState("");
  const suggestions = query
    ? products
        .filter((product) => `${product.name} ${product.categoryLabel}`.toLowerCase().includes(query.toLowerCase()))
        .slice(0, 6)
    : [];

  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2500);
  };

  const formik = useFormik({
    initialValues: { identifier: "" },
    validationSchema: yup.object({
      identifier: yup.string().required("Enter your email or mobile number"),
    }),
    onSubmit: () => {
      setLoading(true);
      window.setTimeout(() => {
        setLoading(false);
        notify("Recovery instructions sent");
      }, 900);
    },
  });

  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) notify("Type a product name");
  };

  return (
    <div className="login-page">
      <PublicHeader
        query={query}
        suggestions={suggestions}
        cartCount={cartCount}
        wishlistCount={wishlistCount}
        onQueryChange={setQuery}
        onSearch={submitSearch}
        onProfile={() => notify("Already on the recovery page")}
        onWishlist={() => router.push("/wishlist")}
        onCart={() => router.push("/cart")}
      />
      <main className="login-main">
        <section className="login-wrapper">
          <div className="login-brand-panel">
            <div className="login-brand-content">
              <div className="login-brand-symbol"><Icon name="lock" /></div>
              <h1>Find your way back to <span>PoojaPoint</span></h1>
              <p>Enter your registered email or mobile number and we&apos;ll help you reset your password securely.</p>
              <div className="login-benefits">
                <div><span><Icon name="shield" /></span>Secure recovery</div>
                <div><span><Icon name="mail" /></span>Simple instructions</div>
                <div><span><Icon name="lock" /></span>Protected account</div>
                <div><span><Icon name="arrow-right" /></span>Back to shopping</div>
              </div>
            </div>
          </div>
          <div className="login-form-panel">
            <div className="login-form-header">
              <h2>Forgot password?</h2>
              <p>We&apos;ll send instructions to help you sign in again.</p>
            </div>
            <form onSubmit={formik.handleSubmit} noValidate>
              <div className={`login-field ${formik.touched.identifier && formik.errors.identifier ? "invalid" : ""}`}>
                <label htmlFor="identifier">Email or mobile number</label>
                <div className="login-input-wrapper">
                  <Icon name="user" />
                  <input id="identifier" {...formik.getFieldProps("identifier")} placeholder="Email or 10-digit mobile" autoComplete="username" maxLength={254} autoFocus />
                </div>
                <small>{formik.touched.identifier && formik.errors.identifier ? formik.errors.identifier : "Enter the details linked to your account."}</small>
              </div>
              <button className="login-submit" type="submit" disabled={loading}>
                {loading ? <span className="login-spinner" /> : <>Send recovery link <Icon name="arrow-right" /></>}
              </button>
              <p className="login-signup">Remember your password? <Link href="/login">Sign in</Link></p>
              <div className="login-security"><Icon name="shield" /> Secure recovery · Your information is protected.</div>
            </form>
          </div>
        </section>
      </main>
      <PublicFooter
        activeNav={nav}
        wishlistCount={wishlistCount}
        cartCount={cartCount}
        onNavChange={setNav}
        onWishlist={() => router.push("/wishlist")}
        onProfile={() => notify("Already on the recovery page")}
      />
      {toast && <div className="toast show">{toast}</div>}
    </div>
  );
}
