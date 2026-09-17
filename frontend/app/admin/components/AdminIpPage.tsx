"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { AdminHeader } from "./AdminHeader";
import { AdminIcon, AdminIconSprite } from "./AdminIcon";
import { AdminSidebar } from "./AdminSidebar";
import { adminApi, type AdminIpPolicy } from "../../../services/api/admin.api";

type IpStatus = "active" | "blocked" | "whitelisted";
type IpRecord = { id: string; ip: string; status: IpStatus; location: string; region: string; note: string; createdAt: string; updatedAt: string };
type IpForm = { ip: string; status: IpStatus; location: string; region: string; note: string };

const emptyForm: IpForm = { ip: "", status: "active", location: "", region: "", note: "" };
const statusName = (value: IpStatus) => value[0].toUpperCase() + value.slice(1);
const formatDate = (value?: string | null) => (value ? new Date(value).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "—");
const toIpPolicy = (policy: AdminIpPolicy): IpRecord => ({
	id: policy.id,
	ip: policy.ipAddress,
	status: policy.status as IpStatus,
	location: policy.location ?? "Unknown",
	region: policy.region ?? "",
	note: policy.note ?? "",
	createdAt: policy.createdAt ?? "",
	updatedAt: policy.updatedAt ?? "",
});

export function AdminIpPage() {
	const [sidebarOpen, setSidebarOpen] = useState(false);
	const [records, setRecords] = useState<IpRecord[]>([]);
	const [loading, setLoading] = useState(true);
	const [query, setQuery] = useState("");
	const [status, setStatus] = useState("all");
	const [modal, setModal] = useState<"view" | "form" | "delete" | "">("");
	const [editing, setEditing] = useState("");
	const [form, setForm] = useState<IpForm>(emptyForm);
	const [target, setTarget] = useState<IpRecord | null>(null);
	const [toast, setToast] = useState("");

	const load = useCallback(() => {
		setLoading(true);
		adminApi
			.listIpPolicies()
			.then(({ ipPolicies }) => setRecords(ipPolicies.map(toIpPolicy)))
			.catch(() => setRecords([]))
			.finally(() => setLoading(false));
	}, []);

	useEffect(() => {
		adminApi
			.listIpPolicies()
			.then(({ ipPolicies }) => setRecords(ipPolicies.map(toIpPolicy)))
			.catch(() => setRecords([]))
			.finally(() => setLoading(false));
	}, []);

	const filtered = useMemo(
		() =>
			records.filter((record) => {
				const term = query.trim().toLowerCase();
				return (
					(!term || `${record.ip} ${record.location} ${record.region} ${record.note}`.toLowerCase().includes(term)) &&
					(status === "all" || record.status === status)
				);
			}),
		[records, query, status],
	);

	const notify = (message: string) => {
		setToast(message);
		window.setTimeout(() => setToast(""), 2300);
	};
	const setField = (key: keyof IpForm, value: string) => setForm((current) => ({ ...current, [key]: value }));
	const openCreate = () => {
		setEditing("");
		setForm({ ...emptyForm });
		setModal("form");
	};
	const openEdit = (record: IpRecord) => {
		setEditing(record.id);
		setForm({ ip: record.ip, status: record.status, location: record.location === "Unknown" ? "" : record.location, region: record.region, note: record.note });
		setModal("form");
	};
	const save = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		const ip = form.ip.trim();
		if (!ip) return;
		const action = editing
			? adminApi.updateIpPolicy(editing, form.status, form.note || undefined)
			: adminApi.createIpPolicy(ip, form.status, form.location || undefined, form.region || undefined, form.note || undefined);
		action
			.then(() => {
				setModal("");
				notify(editing ? "IP policy updated successfully" : "IP policy created successfully");
				load();
			})
			.catch(() => notify("Failed to save IP policy"));
	};
	const toggleBlock = (record: IpRecord) => {
		const blocked = record.status !== "blocked";
		adminApi
			.updateIpPolicy(record.id, blocked ? "blocked" : "active", record.note || undefined)
			.then(() => {
				notify(`${record.ip} has been ${blocked ? "blocked" : "unblocked"}`);
				load();
			})
			.catch(() => notify("Failed to update IP policy"));
	};
	const remove = () => {
		if (!target) return;
		adminApi
			.deleteIpPolicy(target.id)
			.then(() => {
				setModal("");
				notify(`${target.ip} deleted`);
				load();
			})
			.catch(() => notify("Failed to delete IP policy"));
	};
	const exportIps = () => {
		const csv = ["IP,Status,Location,Region,Note,Created", ...filtered.map((item) => `${item.ip},${item.status},${item.location},${item.region},${item.note},${item.createdAt}`)].join("\n");
		const link = document.createElement("a");
		link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
		link.download = "poojapoint-ip-addresses.csv";
		link.click();
		notify("Preparing IP address export...");
	};
	const total = records.length;
	const active = records.filter((record) => record.status === "active").length;
	const blocked = records.filter((record) => record.status === "blocked").length;
	const whitelisted = records.filter((record) => record.status === "whitelisted").length;

	return (
		<div className="admin-dashboard">
			<AdminIconSprite />
			<AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} activeHref="/admin/ip-address" />
			<main className="admin-main">
				<AdminHeader onMenu={() => setSidebarOpen(true)} query={query} onQuery={setQuery} title="IP Addresses" subtitle="Monitor visitor IP activity and protect your PoojaPoint store" />
				<div className="admin-content">
					<div className="ip-exact-page">
						<div className="ip-exact-top">
							<div>
								<div className="ip-exact-heading">IP Address Management</div>
								<div className="ip-exact-description">Monitor traffic, identify suspicious activity and manage blocked addresses.</div>
							</div>
							<div className="ip-exact-actions">
								<button type="button" onClick={exportIps}>
									<AdminIcon name="download" />
									Export
								</button>
								<button className="primary" type="button" onClick={openCreate}>
									<AdminIcon name="plus" />
									Add IP
								</button>
								<button type="button" onClick={load}>
									<AdminIcon name="ip" />
									Refresh
								</button>
							</div>
						</div>
						<section className="ip-exact-summary">
							{[
								["ip", "TOTAL IP ADDRESSES", String(total), "Unique addresses recorded"],
								["check", "ACTIVE IPs", String(active), "Allowed addresses"],
								["ban", "BLOCKED IPs", String(blocked), "Suspicious or restricted"],
								["eye", "WHITELISTED", String(whitelisted), "Trusted addresses"],
							].map(([icon, name, value, note]) => (
								<article key={name}>
									<div>
										<AdminIcon name={icon as "ip" | "check" | "ban" | "eye"} />
									</div>
									<span>{name}</span>
									<strong>{value}</strong>
									<small>{note}</small>
								</article>
							))}
						</section>
						<section className="ip-exact-panel">
							<div className="ip-exact-toolbar">
								<label>
									<AdminIcon name="search" />
									<input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search IP address, location..." />
								</label>
								<select value={status} onChange={(event) => setStatus(event.target.value)}>
									<option value="all">All Status</option>
									<option value="active">Active</option>
									<option value="blocked">Blocked</option>
									<option value="whitelisted">Whitelisted</option>
								</select>
								<span>Showing {filtered.length} addresses</span>
							</div>
							<div className="ip-exact-table-wrap">
								<table className="ip-exact-table">
									<thead>
										<tr>
											{["IP Address", "Location", "Region", "Status", "Note", "Created", "Updated", "Actions"].map((heading) => (
												<th key={heading}>{heading}</th>
											))}
										</tr>
									</thead>
									<tbody>
										{filtered.map((record) => (
											<tr key={record.id}>
												<td>
													<strong>{record.ip}</strong>
													<small>IPv4</small>
												</td>
												<td>
													<b>{record.location}</b>
												</td>
												<td>{record.region || "—"}</td>
												<td>
													<span className={`ip-exact-status ${record.status}`}>{statusName(record.status)}</span>
												</td>
												<td>{record.note || "—"}</td>
												<td>{formatDate(record.createdAt)}</td>
												<td>{formatDate(record.updatedAt)}</td>
												<td>
													<div className="ip-exact-row-actions">
														<button type="button" aria-label={`View ${record.ip}`} onClick={() => { setTarget(record); setModal("view"); }}>
															<AdminIcon name="eye" />
														</button>
														<button type="button" aria-label={`Edit ${record.ip}`} onClick={() => openEdit(record)}>
															<AdminIcon name="edit" />
														</button>
														<button type="button" aria-label={`${record.status === "blocked" ? "Unblock" : "Block"} ${record.ip}`} onClick={() => toggleBlock(record)}>
															<AdminIcon name={record.status === "blocked" ? "check" : "ban"} />
														</button>
														<button className="danger" type="button" aria-label={`Delete ${record.ip}`} onClick={() => { setTarget(record); setModal("delete"); }}>
															<AdminIcon name="trash" />
														</button>
													</div>
												</td>
											</tr>
										))}
									</tbody>
								</table>
								{!filtered.length && <div className="admin-empty-state">{loading ? "Loading IP addresses..." : "No IP addresses match the selected filters."}</div>}
							</div>
							<div className="ip-exact-pagination">
								<span>Showing 1–{filtered.length} of {filtered.length || total} IP addresses</span>
								<div>
									{["‹", "1", "2", "3", "4", "5", "›"].map((value) => (
										<button className={value === "1" ? "active" : ""} type="button" key={value}>
											{value}
										</button>
									))}
								</div>
							</div>
						</section>
					</div>
				</div>
			</main>
			{modal === "view" && target && (
				<div className="ip-exact-modal-overlay" role="presentation" onClick={(event) => event.target === event.currentTarget && setModal("")}>
					<div className="ip-exact-modal">
						<div className="ip-exact-modal-header">
							<div>
								<h2>IP Address Details</h2>
								<p>Policy and traffic information</p>
							</div>
							<button type="button" onClick={() => setModal("")}>
								<AdminIcon name="close" />
							</button>
						</div>
						<div className="ip-exact-modal-body">
							<div className="ip-exact-detail-grid">
								{[
									["IP Address", target.ip],
									["Status", statusName(target.status)],
									["Location", target.location],
									["Region", target.region || "—"],
									["Note", target.note || "—"],
									["Created", formatDate(target.createdAt)],
									["Updated", formatDate(target.updatedAt)],
								].map(([name, value]) => (
									<div key={name}>
										<span>{name}</span>
										<strong>{value}</strong>
									</div>
								))}
							</div>
						</div>
						<div className="ip-exact-modal-footer">
							<button type="button" onClick={() => setModal("")}>
								Close
							</button>
							<button className="primary" type="button" onClick={() => { setModal(""); openEdit(target); }}>
								Edit Policy
							</button>
						</div>
					</div>
				</div>
			)}
			{modal === "form" && (
				<div className="ip-exact-modal-overlay" role="presentation">
					<div className="ip-exact-modal">
						<div className="ip-exact-modal-header">
							<div>
								<h2>{editing ? "Edit IP Policy" : "Add IP Address"}</h2>
								<p>Create or update an IP policy</p>
							</div>
							<button type="button" onClick={() => setModal("")}>
								<AdminIcon name="close" />
							</button>
						</div>
						<form onSubmit={save}>
							<div className="ip-exact-modal-body">
								<div className="ip-exact-form-grid">
									<div className="ip-exact-form-group">
										<label>
											IP Address<span> *</span>
										</label>
										<input required type="text" value={form.ip} onChange={(event) => setField("ip", event.target.value)} placeholder="e.g. 103.84.121.44" disabled={Boolean(editing)} />
									</div>
									<div className="ip-exact-form-group">
										<label>Status</label>
										<select value={form.status} onChange={(event) => setField("status", event.target.value)}>
											<option value="active">Active</option>
											<option value="blocked">Blocked</option>
											<option value="whitelisted">Whitelisted</option>
										</select>
									</div>
									<div className="ip-exact-form-group">
										<label>Location</label>
										<input type="text" value={form.location} onChange={(event) => setField("location", event.target.value)} placeholder="e.g. Hyderabad, India" />
									</div>
									<div className="ip-exact-form-group">
										<label>Region</label>
										<input type="text" value={form.region} onChange={(event) => setField("region", event.target.value)} placeholder="e.g. Telangana" />
									</div>
									<div className="ip-exact-form-group full">
										<label>Note</label>
										<textarea value={form.note} onChange={(event) => setField("note", event.target.value)} placeholder="Reason for blocking, admin notes..." />
									</div>
								</div>
							</div>
							<div className="ip-exact-modal-footer">
								<button type="button" onClick={() => setModal("")}>
									Cancel
								</button>
								<button className="primary" type="submit">
									{editing ? "Save Changes" : "Add IP"}
								</button>
							</div>
						</form>
					</div>
				</div>
			)}
			{modal === "delete" && target && (
				<div className="ip-exact-modal-overlay">
					<div className="ip-exact-modal small">
						<div className="ip-exact-modal-header">
							<div>
								<h2>Delete IP Policy?</h2>
							</div>
							<button type="button" onClick={() => setModal("")}>
								<AdminIcon name="close" />
							</button>
						</div>
						<div className="ip-exact-modal-body">
							<p className="ip-exact-delete-message">Deleting this IP policy will remove it permanently. For most cases, blocking the address is safer than deleting it.</p>
							<div className="ip-exact-delete-name">{target.ip}</div>
						</div>
						<div className="ip-exact-modal-footer">
							<button type="button" onClick={() => setModal("")}>
								Cancel
							</button>
							<button className="danger" type="button" onClick={remove}>
								Delete Policy
							</button>
						</div>
					</div>
				</div>
			)}
			{toast && <div className="coupon-exact-toast show">{toast}</div>}
		</div>
	);
}