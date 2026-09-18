"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { AdminHeader } from "./AdminHeader";
import { AdminIcon, AdminIconSprite } from "./AdminIcon";
import { AdminSidebar } from "./AdminSidebar";
import { adminApi, type AdminCoupon } from "../../../services/api/admin.api";

type Status = "active" | "scheduled" | "expired" | "disabled";
type Type = "percentage" | "fixed";
type Coupon = {
	id: string;
	code: string;
	name: string;
	description: string | null;
	type: Type;
	value: number;
	minimum: number | null;
	usage: number;
	limit: number | null;
	status: Status;
	active: boolean;
	start: string | null;
	end: string | null;
	createdAt: string;
	updatedAt: string;
};
type FormState = { code: string; name: string; type: Type; discount: string; minimum: string; usage: string; start: string; end: string; description: string };

const statusName = (value: Status) => value[0].toUpperCase() + value.slice(1);
const formatMoney = (value: number | null) => (value == null ? "₹0" : `₹${Number(value).toLocaleString("en-IN")}`);
const formatDate = (value?: string | null) => {
	if (!value) return "—";
	return new Date(value).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
};
const toLocalInput = (value?: string | null) => {
	if (!value) return "";
	const date = new Date(value);
	const pad = (n: number) => String(n).padStart(2, "0");
	return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
};
const couponStatus = (coupon: AdminCoupon): Status => {
	if (!coupon.isActive) return "disabled";
	if (coupon.expiresAt && new Date(coupon.expiresAt).getTime() < Date.now()) return "expired";
	if (coupon.startsAt && new Date(coupon.startsAt).getTime() > Date.now()) return "scheduled";
	return "active";
};
const toCoupon = (item: AdminCoupon): Coupon => ({
	id: item.id,
	code: item.code,
	name: item.name ?? item.code,
	description: item.description ?? null,
	type: (item.couponType === "fixed" ? "fixed" : "percentage") as Type,
	value: Number(item.value),
	minimum: item.minimumOrderAmount == null ? null : Number(item.minimumOrderAmount),
	usage: Number(item.usageCount ?? 0),
	limit: item.usageLimit == null ? null : Number(item.usageLimit),
	status: couponStatus(item),
	active: Boolean(item.isActive),
	start: item.startsAt ?? null,
	end: item.expiresAt ?? null,
	createdAt: item.createdAt ?? "",
	updatedAt: item.updatedAt ?? "",
});
const emptyForm: FormState = { code: "", name: "", type: "percentage", discount: "", minimum: "", usage: "", start: "", end: "", description: "" };

export function AdminCouponsPage() {
	const [openSidebar, setOpenSidebar] = useState(false);
	const [list, setList] = useState<Coupon[]>([]);
	const [loading, setLoading] = useState(true);
	const [query, setQuery] = useState("");
	const [status, setStatus] = useState("all");
	const [type, setType] = useState("all");
	const [editing, setEditing] = useState("");
	const [modal, setModal] = useState<"view" | "form" | "delete" | "">("");
	const [selected, setSelected] = useState("");
	const [viewing, setViewing] = useState<Coupon | null>(null);
	const [form, setForm] = useState<FormState>(emptyForm);
	const [formError, setFormError] = useState("");
	const [toast, setToast] = useState("");

	const fetchCoupons = useCallback((showSpinner = false) => {
		if (showSpinner) setLoading(true);
		adminApi
			.listCoupons({ page: 1, pageSize: 100 })
			.then(({ coupons }) => setList(coupons.items.map(toCoupon)))
			.catch(() => setList([]))
			.finally(() => setLoading(false));
	}, []);

	useEffect(() => {
		adminApi
			.listCoupons({ page: 1, pageSize: 100 })
			.then(({ coupons }) => setList(coupons.items.map(toCoupon)))
			.catch(() => setList([]))
			.finally(() => setLoading(false));
	}, [fetchCoupons]);

	const filtered = useMemo(
		() =>
			list.filter((coupon) => {
				const term = query.trim().toLowerCase();
				return (
					(!term || `${coupon.code} ${coupon.name}`.toLowerCase().includes(term)) &&
					(status === "all" || coupon.status === status) &&
					(type === "all" || coupon.type === type)
				);
			}),
		[list, query, status, type],
	);

	const notify = (message: string) => {
		setToast(message);
		window.setTimeout(() => setToast(""), 2300);
	};
	const setField = (key: keyof FormState, value: string) => setForm((current) => ({ ...current, [key]: value }));

	const create = () => {
		setEditing("");
		setForm({ ...emptyForm });
		setFormError("");
		setModal("form");
	};
	const edit = (coupon: Coupon) => {
		setEditing(coupon.id);
		setForm({
			code: coupon.code,
			name: coupon.name,
			type: coupon.type,
			discount: String(coupon.value),
			minimum: coupon.minimum == null ? "" : String(coupon.minimum),
			usage: coupon.limit == null ? "" : String(coupon.limit),
			start: toLocalInput(coupon.start),
			end: toLocalInput(coupon.end),
			description: coupon.description ?? "",
		});
		setFormError("");
		setModal("form");
	};

	const save = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		const code = form.code.trim().toUpperCase();
		const name = form.name.trim();
		const value = Number(form.discount);
		if (!code || !name || !(value > 0)) {
			setFormError("Coupon code, name and a discount value above zero are required.");
			return;
		}
		if (form.type === "percentage" && value > 100) {
			setFormError("Percentage discount cannot exceed 100.");
			return;
		}
		if (form.start && form.end && new Date(form.end).getTime() <= new Date(form.start).getTime()) {
			setFormError("Expiry date must be after the start date.");
			return;
		}
		const data: Record<string, unknown> = {
			code,
			name,
			description: form.description.trim() || null,
			couponType: form.type,
			value,
			minimumOrderAmount: form.minimum ? Number(form.minimum) : null,
			maximumDiscount: null,
			startsAt: form.start ? new Date(form.start).toISOString() : null,
			expiresAt: form.end ? new Date(form.end).toISOString() : null,
			usageLimit: form.usage ? Number(form.usage) : null,
			perUserLimit: null,
			isActive: true,
		};
		const action = editing ? adminApi.updateCoupon(editing, data) : adminApi.createCoupon(data);
		action
			.then(() => {
				setModal("");
				setFormError("");
				notify(editing ? "Coupon updated successfully" : "Coupon created successfully");
				fetchCoupons();
			})
			.catch((error) => {
				setFormError(error instanceof Error ? error.message : "Failed to save coupon. Please try again.");
			});
	};

	const remove = () => {
		if (!selected) return;
		adminApi
			.deleteCoupon(selected)
			.then(() => {
				setModal("");
				notify("Coupon deleted successfully");
				fetchCoupons();
			})
			.catch(() => notify("Failed to delete coupon"));
	};

	const toggleActive = (coupon: Coupon) => {
		adminApi
			.setCouponActive(coupon.id, !coupon.active)
			.then(() => {
				notify(coupon.active ? `${coupon.code} disabled` : `${coupon.code} activated`);
				fetchCoupons();
			})
			.catch(() => notify("Failed to update coupon status"));
	};

	const duplicate = (coupon: Coupon) => {
		const data: Record<string, unknown> = {
			code: `${coupon.code}-COPY`,
			name: `${coupon.name} Copy`,
			description: coupon.description,
			couponType: coupon.type,
			value: coupon.value,
			minimumOrderAmount: coupon.minimum,
			maximumDiscount: null,
			startsAt: coupon.start ? new Date(coupon.start).toISOString() : null,
			expiresAt: coupon.end ? new Date(coupon.end).toISOString() : null,
			usageLimit: coupon.limit,
			perUserLimit: null,
			isActive: false,
		};
		adminApi
			.createCoupon(data)
			.then(() => {
				notify(`${coupon.code} duplicated successfully`);
				fetchCoupons();
			})
			.catch(() => notify("Failed to duplicate coupon"));
	};

	const exportCoupons = () => {
		const csv = ["Code,Name,Type,Discount,Minimum Order,Usage,Limit,Status", ...filtered.map((item) => `${item.code},${item.name},${item.type},${item.value},${formatMoney(item.minimum)},${item.usage},${item.limit ?? "Unlimited"},${statusName(item.status)}`)].join("\n");
		const link = document.createElement("a");
		link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
		link.download = "poojapoint-coupons.csv";
		link.click();
		notify("Preparing coupon export...");
	};

	const totalCoupons = list.length;
	const activeCoupons = list.filter((coupon) => coupon.active).length;
	const totalUsage = list.reduce((sum, coupon) => sum + coupon.usage, 0);
	const activeNow = list.filter((coupon) => coupon.status === "active").length;

	return (
		<div className="admin-dashboard">
			<AdminIconSprite />
			<AdminSidebar open={openSidebar} onClose={() => setOpenSidebar(false)} activeHref="/admin/coupons" />
			<main className="admin-main">
				<AdminHeader onMenu={() => setOpenSidebar(true)} query={query} onQuery={setQuery} title="Coupons" subtitle="Create and manage PoojaPoint discounts" />
				<div className="admin-content">
					<div className="coupon-exact-page">
						<div className="coupon-exact-top">
							<div>
								<div className="coupon-exact-heading">Coupon Management</div>
								<div className="coupon-exact-description">Create powerful offers and manage promotional discounts.</div>
							</div>
							<button className="coupon-exact-primary" type="button" onClick={create}>
								<AdminIcon name="plus" />
								Create Coupon
							</button>
						</div>
						<section className="coupon-exact-stats">
							{[
								["discount", "Total Coupons", String(totalCoupons)],
								["discount", "Active Coupons", String(activeCoupons)],
								["orders", "Total Uses", String(totalUsage)],
								["discount", "Active Now", String(activeNow)],
							].map(([icon, name, value]) => (
								<div className="coupon-exact-stat" key={name}>
									<div className="coupon-exact-stat-icon">
										<AdminIcon name={icon as "discount" | "orders"} />
									</div>
									<div>
										<div className="coupon-exact-stat-label">{name}</div>
										<div className="coupon-exact-stat-value">{value}</div>
									</div>
								</div>
							))}
						</section>
						<section className="coupon-exact-panel">
							<div className="coupon-exact-toolbar">
								<div className="coupon-exact-toolbar-left">
									<label className="coupon-exact-search">
										<AdminIcon name="search" />
										<input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search code or coupon name..." />
									</label>
									<select className="coupon-exact-select" value={status} onChange={(event) => setStatus(event.target.value)}>
										<option value="all">All Status</option>
										<option value="active">Active</option>
										<option value="scheduled">Scheduled</option>
										<option value="expired">Expired</option>
										<option value="disabled">Disabled</option>
									</select>
									<select className="coupon-exact-select" value={type} onChange={(event) => setType(event.target.value)}>
										<option value="all">All Discount Types</option>
										<option value="percentage">Percentage</option>
										<option value="fixed">Fixed Amount</option>
									</select>
								</div>
								<div className="coupon-exact-toolbar-right">
									<button className="coupon-exact-tool" type="button" onClick={() => fetchCoupons(true)}>
										<AdminIcon name="ip" />
										Refresh
									</button>
									<button className="coupon-exact-tool" type="button" onClick={exportCoupons}>
										<AdminIcon name="download" />
										Export
									</button>
								</div>
							</div>
							<div className="coupon-exact-table-wrap">
								<table className="coupon-exact-table">
									<thead>
										<tr>
											{["Coupon", "Discount", "Minimum Order", "Usage", "Validity", "Status", "Active", "Actions"].map((heading) => (
												<th key={heading}>{heading}</th>
											))}
										</tr>
									</thead>
									<tbody>
										{filtered.map((coupon) => (
											<tr key={coupon.id}>
												<td>
													<div className="coupon-exact-code">{coupon.code}</div>
													<div className="coupon-exact-name">{coupon.name}</div>
												</td>
												<td>
													<div className="coupon-exact-discount">{coupon.type === "fixed" ? formatMoney(coupon.value) : `${coupon.value}%`}</div>
													<div className="coupon-exact-sub">{coupon.type === "fixed" ? "Fixed discount" : "Percentage discount"}</div>
												</td>
												<td>
													<div className="coupon-exact-date-main">{formatMoney(coupon.minimum)}</div>
													<div className="coupon-exact-sub">Minimum cart value</div>
												</td>
												<td>
													<div className="coupon-exact-usage">{coupon.usage}</div>
													<div className="coupon-exact-sub">{coupon.limit == null ? "Unlimited" : `of ${coupon.limit} uses`}</div>
												</td>
												<td>
													<div className="coupon-exact-date-main">
														{formatDate(coupon.start)} – {formatDate(coupon.end)}
													</div>
												</td>
												<td>
													<span className={`coupon-exact-status ${coupon.status}`}>{statusName(coupon.status)}</span>
												</td>
												<td>
													<button className={`coupon-exact-toggle ${coupon.active ? "active" : ""}`} type="button" aria-label={`Toggle ${coupon.code}`} onClick={() => toggleActive(coupon)} />
												</td>
												<td>
													<div className="coupon-exact-actions">
														<button className="coupon-exact-action" type="button" aria-label={`View ${coupon.code}`} onClick={() => { setViewing(coupon); setModal("view"); }}>
															<AdminIcon name="eye" />
														</button>
														<button className="coupon-exact-action" type="button" aria-label={`Edit ${coupon.code}`} onClick={() => edit(coupon)}>
															<AdminIcon name="edit" />
														</button>
														<button className="coupon-exact-action" type="button" aria-label={`Duplicate ${coupon.code}`} onClick={() => duplicate(coupon)}>
															<AdminIcon name="copy" />
														</button>
														<button className="coupon-exact-action delete" type="button" aria-label={`Delete ${coupon.code}`} onClick={() => { setSelected(coupon.id); setModal("delete"); }}>
															<AdminIcon name="trash" />
														</button>
													</div>
												</td>
											</tr>
										))}
									</tbody>
								</table>
								{!filtered.length && <div className="admin-empty-state">{loading ? "Loading coupons..." : "No coupons match the selected filters."}</div>}
							</div>
							<div className="coupon-exact-pagination">
								<div className="coupon-exact-pagination-info">
									Showing 1–{filtered.length} of {list.length || 0} coupons
								</div>
								<div className="coupon-exact-pages">
									{["‹", "1", "2", "3", "4", "5", "›"].map((item) => (
										<button className={`coupon-exact-page-button ${item === "1" ? "active" : ""}`} type="button" key={item}>
											{item}
										</button>
									))}
								</div>
							</div>
						</section>
					</div>
				</div>
			</main>
			{modal === "view" && viewing && (
				<div className="coupon-exact-modal-overlay" role="presentation" onClick={(event) => event.target === event.currentTarget && setModal("")}>
					<div className="coupon-exact-modal">
						<div className="coupon-exact-modal-header">
							<div>
								<div className="coupon-exact-modal-title">Coupon Details</div>
								<div className="coupon-exact-modal-subtitle">{viewing.code} — {statusName(viewing.status)}</div>
							</div>
							<button className="coupon-exact-modal-close" type="button" onClick={() => setModal("")}>
								<AdminIcon name="close" />
							</button>
						</div>
						<div className="coupon-exact-modal-body">
							<div className="coupon-exact-form-grid">
								{[
									["Coupon Code", viewing.code],
									["Coupon Name", viewing.name],
									["Type", viewing.type === "fixed" ? "Fixed Amount" : "Percentage"],
									["Value", viewing.type === "fixed" ? formatMoney(viewing.value) : `${viewing.value}%`],
									["Minimum Order", formatMoney(viewing.minimum)],
									["Usage", `${viewing.usage}${viewing.limit == null ? "" : ` / ${viewing.limit}`}`],
									["Start Date", formatDate(viewing.start)],
									["Expiry Date", formatDate(viewing.end)],
									["Status", statusName(viewing.status)],
								].map(([name, value]) => (
									<div key={name}>
										<span>{name}</span>
										<strong>{value}</strong>
									</div>
								))}
							</div>
							{viewing.description && <p className="coupon-exact-description">{viewing.description}</p>}
						</div>
						<div className="coupon-exact-modal-footer">
							<button className="coupon-exact-modal-button" type="button" onClick={() => setModal("")}>
								Close
							</button>
							<button className="coupon-exact-modal-button primary" type="button" onClick={() => { setModal(""); edit(viewing); }}>
								Edit Coupon
							</button>
						</div>
					</div>
				</div>
			)}
			{modal === "form" && (
				<div className="coupon-exact-modal-overlay" role="presentation">
					<div className="coupon-exact-modal">
						<div className="coupon-exact-modal-header">
							<div>
								<div className="coupon-exact-modal-title">{editing ? "Edit Coupon" : "Create Coupon"}</div>
								<div className="coupon-exact-modal-subtitle">Create a promotional discount for customers</div>
							</div>
							<button className="coupon-exact-modal-close" type="button" onClick={() => setModal("")}>
								<AdminIcon name="close" />
							</button>
						</div>
						<form onSubmit={save} noValidate>
							<div className="coupon-exact-modal-body">
								{formError && <div className="coupon-exact-delete-message">{formError}</div>}
								<div className="coupon-exact-form-grid">
									<div className="coupon-exact-form-group full">
										<label className="coupon-exact-label">
											Coupon Code<span> *</span>
										</label>
										<input className="coupon-exact-code-input" required value={form.code} onChange={(event) => setField("code", event.target.value)} placeholder="WELCOME10" disabled={Boolean(editing)} />
									</div>
									<div className="coupon-exact-form-group">
										<label className="coupon-exact-label">
											Coupon Name<span> *</span>
										</label>
										<input className="coupon-exact-form-input" required value={form.name} onChange={(event) => setField("name", event.target.value)} placeholder="New Customer Offer" />
									</div>
									<div className="coupon-exact-form-group">
										<label className="coupon-exact-label">
											Discount Value<span> *</span>
										</label>
										<input className="coupon-exact-form-input" required type="number" min="0" step="0.01" value={form.discount} onChange={(event) => setField("discount", event.target.value)} placeholder="10" />
									</div>
									<div className="coupon-exact-form-group">
										<label className="coupon-exact-label">Minimum Order Value</label>
										<input className="coupon-exact-form-input" type="number" min="0" step="0.01" value={form.minimum} onChange={(event) => setField("minimum", event.target.value)} placeholder="499" />
									</div>
									<div className="coupon-exact-form-group">
										<label className="coupon-exact-label">Total Usage Limit</label>
										<input className="coupon-exact-form-input" type="number" min="1" value={form.usage} onChange={(event) => setField("usage", event.target.value)} placeholder="500" />
									</div>
									<div className="coupon-exact-form-group">
										<label className="coupon-exact-label">Discount Type <span>*</span></label>
										<select className="coupon-exact-form-select" value={form.type} onChange={(event) => setField("type", event.target.value)}>
											<option value="percentage">Percentage Discount</option>
											<option value="fixed">Fixed Amount</option>
										</select>
									</div>
									<div className="coupon-exact-form-group">
										<label className="coupon-exact-label">Start Date</label>
										<input className="coupon-exact-form-input" type="datetime-local" value={form.start} onChange={(event) => setField("start", event.target.value)} />
									</div>
									<div className="coupon-exact-form-group">
										<label className="coupon-exact-label">Expiry Date</label>
										<input className="coupon-exact-form-input" type="datetime-local" value={form.end} onChange={(event) => setField("end", event.target.value)} />
									</div>
									<div className="coupon-exact-form-group full">
										<label className="coupon-exact-label">Coupon Description</label>
										<textarea className="coupon-exact-form-textarea" value={form.description} onChange={(event) => setField("description", event.target.value)} placeholder="Describe this offer for internal reference..." />
									</div>
								</div>
							</div>
							<div className="coupon-exact-modal-footer">
								<button className="coupon-exact-modal-button" type="button" onClick={() => setModal("")}>
									Cancel
								</button>
								<button className="coupon-exact-modal-button primary" type="submit">
									Save Coupon
								</button>
							</div>
						</form>
					</div>
				</div>
			)}
			{modal === "delete" && (
				<div className="coupon-exact-modal-overlay" role="presentation">
					<div className="coupon-exact-modal small">
						<div className="coupon-exact-modal-header">
							<div className="coupon-exact-modal-title">Delete Coupon?</div>
							<button className="coupon-exact-modal-close" type="button" onClick={() => setModal("")}>
								<AdminIcon name="close" />
							</button>
						</div>
						<div className="coupon-exact-modal-body">
							<div className="coupon-exact-delete-message">Deleting a coupon permanently removes it from your promotion system. Expired coupons can be kept for reporting instead.</div>
							<div className="coupon-exact-delete-code">{list.find((coupon) => coupon.id === selected)?.code ?? ""}</div>
						</div>
						<div className="coupon-exact-modal-footer">
							<button className="coupon-exact-modal-button" type="button" onClick={() => setModal("")}>
								Cancel
							</button>
							<button className="coupon-exact-modal-button danger" type="button" onClick={remove}>
								Delete Coupon
							</button>
						</div>
					</div>
				</div>
			)}
			{toast && <div className="coupon-exact-toast show">{toast}</div>}
		</div>
	);
}