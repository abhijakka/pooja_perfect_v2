"use client";

import { useEffect, useMemo, useState } from "react";
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
import { products } from "../../(public)/storefront-data";
import { accountApi, type AccountOrder } from "../../../services/api/account.api";
import { authApi } from "../../../services/api/auth.api";
import { useAppDispatch } from "../../../store/hooks";
import { logout } from "../../../store/slices/authSlice";

type Address = { id: string; type: string; name: string; line: string; city: string; phone: string; default?: boolean };
type Modal = "profile" | "address" | "password" | "security" | "delete" | null;

function money(value: number) {
	return `₹${value.toLocaleString("en-IN")}`;
}

export default function AccountPage() {
	const router = useRouter();
	const dispatch = useAppDispatch();
	const { count: cartCount } = useCart();
	const { count: wishlistCount } = useWishlist();
	const [query, setQuery] = useState("");
	const [nav, setNav] = useState("profile");
	const [modal, setModal] = useState<Modal>(null);
	const [toast, setToast] = useState("");
	const [profile, setProfile] = useState({ name: "", email: "", phone: "", dob: "" });
	const [addresses, setAddresses] = useState<Address[]>([]);
	const [recentOrders, setRecentOrders] = useState<AccountOrder[]>([]);
	useEffect(() => {
		accountApi.getOverview().then(({ current_user, addresses: result, orders }) => {
			setProfile({ name: `${current_user.first_name} ${current_user.last_name}`.trim(), email: current_user.email, phone: current_user.phone ?? "", dob: "" });
			setAddresses(result.map((address) => ({ id: address.id, type: address.label, name: address.recipient_name, line: address.address_line1, city: `${address.city}, ${address.state} - ${address.postal_code}, ${address.country}`, phone: address.phone, default: address.is_default })));
			setRecentOrders(orders.items);
		}).catch(() => setToast("Account data could not be loaded"));
	}, []);
	const [editingAddress, setEditingAddress] = useState<Address | null>(null);
	const [preferences, setPreferences] = useState({ orders: true, offers: true, whatsapp: false, email: true });
	const [securityPreferences, setSecurityPreferences] = useState({ alerts: true, twoFactor: false });
	const suggestions = useMemo(() => query ? products.filter((item) => `${item.name} ${item.categoryLabel}`.toLowerCase().includes(query.toLowerCase())).slice(0, 6) : [], [query]);

	const notify = (message: string) => {
		setToast(message);
		window.setTimeout(() => setToast(""), 2200);
	};
	const closeModal = () => setModal(null);
	const profileForm = useFormik({
		initialValues: { name: "", email: "", phone: "", dob: "" },
		validationSchema: yup.object({
			name: name.required("Enter your full name"),
			email: email.required("Enter your email address"),
			phone: phone.required("Enter your phone number"),
			dob: yup.string(),
		}),
		onSubmit: (values) => { setProfile(values); closeModal(); notify("Profile updated successfully"); },
	});
	const addressForm = useFormik({
		initialValues: { type: "Home", name: "", line: "", city: "", phone: "" },
		validationSchema: yup.object({
			type: yup.string(),
			name: name.required("Enter your full name"),
			line: yup.string().required("Enter your address"),
			city: yup.string().required("Enter your city and state"),
			phone: phone.required("Enter your phone number"),
		}),
		onSubmit: (values) => {
			if (editingAddress) setAddresses((current) => current.map((address) => address.id === editingAddress.id ? { ...address, ...values } : address));
			else setAddresses((current) => [...current, { ...values, id: String(Date.now()) }]);
			closeModal(); notify(editingAddress ? "Address updated successfully" : "Address added successfully");
		},
	});
	const passwordForm = useFormik({
		initialValues: { current: "", next: "", confirm: "" },
		validationSchema: yup.object({
			current: yup.string().required("Enter your current password"),
			next: password.required("Enter a new password"),
			confirm: yup.string().oneOf([yup.ref("next")], "Passwords do not match").required("Confirm your password"),
		}),
		onSubmit: () => { closeModal(); notify("Password updated successfully"); },
	});
	const openProfile = () => { profileForm.setValues(profile); setModal("profile"); };
	const openAddress = (address?: Address) => {
		setEditingAddress(address ?? null);
		addressForm.setValues(address ? { type: address.type, name: address.name, line: address.line, city: address.city, phone: address.phone } : { type: "Home", name: "", line: "", city: "", phone: "" });
		setModal("address");
	};
	const deleteAddress = (id: string) => {
		if (!window.confirm("Delete this saved address?")) return;
		setAddresses((current) => current.filter((address) => address.id !== id));
		notify("Address deleted");
	};
	const submitSearch = (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); if (!query.trim()) notify("Type a product name"); };
	const signOut = async () => {
		try { await authApi.logout(); } finally { dispatch(logout()); router.replace("/"); }
	};

	return <>
		<PublicHeader query={query} suggestions={suggestions} cartCount={cartCount} wishlistCount={wishlistCount} onQueryChange={setQuery} onSearch={submitSearch} onProfile={openProfile} onWishlist={() => router.push("/wishlist")} onCart={() => router.push("/cart")} />
		<main className="my-account-page">
			<div className="breadcrumb"><Link href="/">Home</Link><span>›</span>My Account</div>
			<section className="account-hero"><div className="account-profile"><div className="account-avatar"><Icon name="user" /></div><div><small>Welcome back</small><h1>{profile.name}</h1><p>{profile.email}</p></div></div><button className="account-edit-button" onClick={openProfile}><Icon name="plus" /> Edit Profile</button></section>
			<section className="account-grid"><aside className="account-sidebar"><button className="account-side-item active"><Icon name="user" /> My Account</button><Link className="account-side-item" href="/my-orders"><Icon name="box" /> My Orders</Link><Link className="account-side-item" href="/wishlist"><Icon name="heart" /> Wishlist <span>{wishlistCount}</span></Link><a className="account-side-item" href="#address"><Icon name="location" /> Addresses</a><button className="account-side-item" onClick={() => setModal("security")}><Icon name="shield" /> Security</button><a className="account-side-item" href="#preferences"><Icon name="check" /> Notifications</a><div className="account-side-divider" /><button className="account-side-item danger" onClick={() => { if (window.confirm("Are you sure you want to sign out?")) void signOut(); }}><Icon name="arrow-right" /> Sign Out</button></aside>
				<div className="account-content"><div className="account-quick-grid"><Link href="/my-orders" className="account-quick-card"><div><Icon name="box" /></div><strong>4</strong><span>Total Orders</span></Link><Link href="/my-orders" className="account-quick-card"><div><Icon name="truck" /></div><strong>1</strong><span>On the Way</span></Link><Link href="/wishlist" className="account-quick-card"><div><Icon name="heart" /></div><strong>{wishlistCount}</strong><span>Wishlist</span></Link><a href="#address" className="account-quick-card"><div><Icon name="location" /></div><strong>{addresses.length}</strong><span>Saved Addresses</span></a></div>
					<section className="account-card"><div className="account-card-header"><h2>Personal information</h2><button onClick={openProfile}>Edit</button></div><div className="account-details-grid">{[["Full name", profile.name], ["Email address", profile.email], ["Phone number", profile.phone], ["Date of birth", profile.dob || "Not added"], ["Account created", "August 2026"], ["Account status", "● Active"]].map(([label, value]) => <div key={label}><span>{label}</span><strong className={label === "Date of birth" ? "light" : label === "Account status" ? "green" : ""}>{value}</strong></div>)}</div></section>
					<section className="account-card" id="address"><div className="account-card-header"><h2>Saved addresses</h2><button onClick={() => openAddress()}>+ Add New</button></div>{addresses.map((address) => <div className="saved-address" key={address.id}><div className="saved-address-icon"><Icon name="location" /></div><div className="saved-address-info"><strong>{address.type} {address.default && <small>Default</small>}</strong><p>{address.name}<br />{address.line}<br />{address.city}<br />{address.phone}</p></div><div className="saved-address-actions"><button onClick={() => openAddress(address)}>Edit</button><button className="danger" onClick={() => deleteAddress(address.id)}>Delete</button></div></div>)}</section>
					<section className="account-card"><div className="account-card-header"><h2>Recent orders</h2><Link href="/my-orders">View All</Link></div>{recentOrders.map((order) => <Link className="account-order-row" href={`/order/track?order=${order.id}`} key={order.id}><div className="account-order-image"><Icon name={order.status.toLowerCase().includes("deliver") ? "check" : "box"} /></div><div className="account-order-info"><strong>{order.order_number}</strong><span>{order.items.reduce((count, item) => count + item.quantity, 0)} items · {new Date(order.created_at).toLocaleDateString("en-IN")}</span></div><span className={`account-order-status ${order.status.toLowerCase() === "processing" ? "processing" : ""}`}>{order.status}</span><strong className="account-order-price">{money(Number(order.total))}</strong></Link>)}</section>
					<section className="account-card" id="security"><div className="account-card-header"><h2>Security</h2><button onClick={() => setModal("security")}>Manage</button></div><div className="account-security-row"><div><Icon name="lock" /></div><p><strong>Password</strong><span>Change your account password regularly for better security.</span></p><button onClick={() => setModal("password")}>Change</button></div><div className="account-security-row"><div><Icon name="shield" /></div><p><strong>Login protection</strong><span>Your account is protected.</span></p><em>Active</em></div></section>
					<section className="account-card" id="preferences"><div className="account-card-header"><h2>Notifications & preferences</h2></div>{([["orders", "Order updates", "Get delivery and order status updates."], ["offers", "Offers & new products", "Receive occasional PoojaPoint offers."], ["whatsapp", "WhatsApp notifications", "Receive important updates on WhatsApp."], ["email", "Email notifications", "Receive account and shopping updates by email."]] as const).map(([key, title, text]) => <div className="account-preference" key={key}><p><strong>{title}</strong><span>{text}</span></p><button className={`account-toggle ${preferences[key] ? "active" : ""}`} onClick={() => setPreferences((current) => ({ ...current, [key]: !current[key] }))} aria-label={`Toggle ${title}`} /></div>)}</section>
					<section className="account-support"><div><h2>We are here to help</h2><p>Need help with an order, payment, return or anything else? Our support team is happy to assist you.</p></div><a href="mailto:support@poojapoint.com">Contact Support</a></section>
					<section className="account-card"><div className="account-card-header"><h2>Account</h2></div><div className="account-danger"><h3>Delete account</h3><p>Permanently remove your account and personal profile information. This action requires password confirmation.</p><button onClick={() => setModal("delete")}><Icon name="trash" /> Delete My Account</button></div></section>
				</div></section>
		</main>
		<PublicFooter activeNav={nav} wishlistCount={wishlistCount} cartCount={cartCount} onNavChange={setNav} onWishlist={() => router.push("/wishlist")} onProfile={openProfile} />
		{toast && <div className="toast show">{toast}</div>}
		{modal && <div className="account-modal-overlay" onMouseDown={(event) => { if (event.target === event.currentTarget) closeModal(); }}><div className="account-modal"><div className="account-modal-header"><h2>{modal === "profile" ? "Edit profile" : modal === "address" ? (editingAddress ? "Edit address" : "Add address") : modal === "password" ? "Change password" : modal === "security" ? "Security settings" : "Delete account"}</h2><button onClick={closeModal} aria-label="Close dialog">×</button></div>{modal === "profile" && <form onSubmit={profileForm.handleSubmit} className="account-form"><label>Full name<input {...profileForm.getFieldProps("name")} required />{profileForm.touched.name && profileForm.errors.name && <small className="form-error">{profileForm.errors.name}</small>}</label><label>Email address<input type="email" {...profileForm.getFieldProps("email")} required />{profileForm.touched.email && profileForm.errors.email && <small className="form-error">{profileForm.errors.email}</small>}</label><label>Phone number<input {...profileForm.getFieldProps("phone")} required />{profileForm.touched.phone && profileForm.errors.phone && <small className="form-error">{profileForm.errors.phone}</small>}</label><label>Date of birth<input type="date" {...profileForm.getFieldProps("dob")} /></label><div className="account-modal-actions"><button type="button" onClick={closeModal}>Cancel</button><button type="submit">Save Changes</button></div></form>}{modal === "address" && <form onSubmit={addressForm.handleSubmit} className="account-form"><label>Address type<select {...addressForm.getFieldProps("type")}><option>Home</option><option>Office</option><option>Other</option></select></label><label>Full name<input {...addressForm.getFieldProps("name")} required />{addressForm.touched.name && addressForm.errors.name && <small className="form-error">{addressForm.errors.name}</small>}</label><label>Address<input {...addressForm.getFieldProps("line")} required />{addressForm.touched.line && addressForm.errors.line && <small className="form-error">{addressForm.errors.line}</small>}</label><label>City and state<input {...addressForm.getFieldProps("city")} required />{addressForm.touched.city && addressForm.errors.city && <small className="form-error">{addressForm.errors.city}</small>}</label><label>Phone<input {...addressForm.getFieldProps("phone")} required />{addressForm.touched.phone && addressForm.errors.phone && <small className="form-error">{addressForm.errors.phone}</small>}</label><div className="account-modal-actions"><button type="button" onClick={closeModal}>Cancel</button><button type="submit">Save Address</button></div></form>}{modal === "password" && <form onSubmit={passwordForm.handleSubmit} className="account-form"><label>Current password<input type="password" {...passwordForm.getFieldProps("current")} required />{passwordForm.touched.current && passwordForm.errors.current && <small className="form-error">{passwordForm.errors.current}</small>}</label><label>New password<input type="password" {...passwordForm.getFieldProps("next")} required />{passwordForm.touched.next && passwordForm.errors.next && <small className="form-error">{passwordForm.errors.next}</small>}</label><label>Confirm password<input type="password" {...passwordForm.getFieldProps("confirm")} required />{passwordForm.touched.confirm && passwordForm.errors.confirm && <small className="form-error">{passwordForm.errors.confirm}</small>}</label><div className="account-modal-actions"><button type="button" onClick={closeModal}>Cancel</button><button type="submit">Update Password</button></div></form>}{modal === "security" && <div className="account-modal-settings"><div><span>Login alerts</span><button className={`account-toggle ${securityPreferences.alerts ? "active" : ""}`} onClick={() => setSecurityPreferences((current) => ({ ...current, alerts: !current.alerts }))} /></div><div><span>Two-step verification</span><button className={`account-toggle ${securityPreferences.twoFactor ? "active" : ""}`} onClick={() => setSecurityPreferences((current) => ({ ...current, twoFactor: !current.twoFactor }))} /></div><button className="account-modal-primary" onClick={closeModal}>Done</button></div>}{modal === "delete" && <div className="account-delete-modal"><p>This action cannot be undone. Your profile and personal account information will be removed.</p><input type="password" placeholder="Enter your password" /><div className="account-modal-actions"><button onClick={closeModal}>Keep Account</button><button className="danger" onClick={() => { closeModal(); notify("Account deletion requested"); }}>Delete Account</button></div></div>}</div></div>}
	</>;
}
