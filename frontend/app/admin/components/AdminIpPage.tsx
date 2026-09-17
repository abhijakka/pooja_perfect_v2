"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { AdminHeader } from "./AdminHeader";
import { AdminIcon, AdminIconSprite } from "./AdminIcon";
import { AdminSidebar } from "./AdminSidebar";
import { adminApi, type AdminIpActivity, type AdminIpPolicy } from "../../../services/api/admin.api";

type DeviceType = "desktop" | "mobile" | "tablet" | "unknown";
type PolicyStatus = "open" | "active" | "blocked" | "whitelisted";
type IpRecord = { id: string; ip: string; action: string; device: string; deviceType: DeviceType; os: string; browser: string; page: string; visits: number; createdAt: string; updatedAt: string };
type IpForm = { ip: string; page: string; device: string; deviceType: DeviceType; os: string; browser: string; visits: string };

const emptyForm: IpForm = { ip: "", page: "/", device: "", deviceType: "desktop", os: "", browser: "", visits: "1" };
const deviceTypeName = (value: DeviceType) => value[0].toUpperCase() + value.slice(1);
const policyStatusName = (value: PolicyStatus) => (value === "open" ? "Open" : value[0].toUpperCase() + value.slice(1));
const formatDate = (value?: string | null) => (value ? new Date(value).toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "—");
const toIpRecord = (item: AdminIpActivity): IpRecord => ({
	id: item.id,
	ip: item.ipAddress,
	action: item.action || "page_view",
	device: item.device ?? (item.deviceType ? deviceTypeName(item.deviceType as DeviceType) : "Unknown"),
	deviceType: (item.deviceType as DeviceType) || "unknown",
	os: item.os ?? "Unknown",
	browser: item.browser ?? "Unknown",
	page: item.path || "/",
	visits: item.visitCount ?? 1,
	createdAt: item.createdAt ?? "",
	updatedAt: item.updatedAt ?? "",
});

export function AdminIpPage() {
	const [sidebarOpen, setSidebarOpen] = useState(false);
	const [records, setRecords] = useState<IpRecord[]>([]);
	const [policies, setPolicies] = useState<AdminIpPolicy[]>([]);
	const [total, setTotal] = useState(0);
	const [loading, setLoading] = useState(true);
	const [query, setQuery] = useState("");
	const [device, setDevice] = useState("all");
	const [status, setStatus] = useState("all");
	const [modal, setModal] = useState<"view" | "form" | "delete" | "">("");
	const [editing, setEditing] = useState("");
	const [form, setForm] = useState<IpForm>(emptyForm);
	const [target, setTarget] = useState<IpRecord | null>(null);
	const [toast, setToast] = useState("");

	const policyByIp = useMemo(() => new Map(policies.map((policy) => [policy.ipAddress, policy])), [policies]);
	const statusOf = useCallback((ip: string): PolicyStatus => (policyByIp.get(ip)?.status as PolicyStatus) ?? "open", [policyByIp]);
	const isBlocked = useCallback((ip: string) => statusOf(ip) === "blocked", [statusOf]);

	const fetchRecords = useCallback((showSpinner = false) => {
		if (showSpinner) setLoading(true);
		Promise.all([
			adminApi.listIpActivity({ page: 1, pageSize: 100 }),
			adminApi.listIpPolicies().catch(() => ({ ipPolicies: [] as AdminIpPolicy[] })),
		])
			.then(([{ ipActivity }, { ipPolicies }]) => {
				setRecords(ipActivity.items.map(toIpRecord));
				setPolicies(ipPolicies);
				setTotal(ipActivity.pagination?.total ?? ipActivity.items.length);
			})
			.catch(() => {
				setRecords([]);
				setPolicies([]);
			})
			.finally(() => setLoading(false));
	}, []);

	useEffect(() => {
		Promise.all([
			adminApi.listIpActivity({ page: 1, pageSize: 100 }),
			adminApi.listIpPolicies().catch(() => ({ ipPolicies: [] as AdminIpPolicy[] })),
		])
			.then(([{ ipActivity }, { ipPolicies }]) => {
				setRecords(ipActivity.items.map(toIpRecord));
				setPolicies(ipPolicies);
				setTotal(ipActivity.pagination?.total ?? ipActivity.items.length);
			})
			.catch(() => {
				setRecords([]);
				setPolicies([]);
			})
			.finally(() => setLoading(false));
	}, []);

	const filtered = useMemo(
		() =>
			records.filter((record) => {
				const term = query.trim().toLowerCase();
				return (
					(!term || `${record.ip} ${record.device} ${record.os} ${record.browser} ${record.page}`.toLowerCase().includes(term)) &&
					(device === "all" || record.deviceType === device) &&
					(status === "all" || statusOf(record.ip) === status)
				);
			}),
		[records, query, device, status, statusOf],
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
		setForm({ ip: record.ip, page: record.page, device: record.device === "Unknown" ? "" : record.device, deviceType: record.deviceType, os: record.os === "Unknown" ? "" : record.os, browser: record.browser === "Unknown" ? "" : record.browser, visits: String(record.visits) });
		setModal("form");
	};
	const save = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		const ip = form.ip.trim();
		if (!ip) return;
		const visits = Math.max(1, Number(form.visits) || 1);
		const page = form.page.trim() || "/";
		const action = editing
			? adminApi.updateIpActivity(editing, { path: page, visitCount: visits, browser: form.browser.trim() || undefined, os: form.os.trim() || undefined, device: form.device.trim() || undefined, deviceType: form.deviceType })
			: adminApi.createIpActivity(ip, page, visits, form.browser.trim() || undefined, form.os.trim() || undefined, form.device.trim() || undefined, form.deviceType);
		action
			.then(() => {
				setModal("");
				notify(editing ? "Visit record updated successfully" : "Visit record created successfully");
				fetchRecords();
			})
			.catch(() => notify("Failed to save visit record"));
	};
	const remove = () => {
		if (!target) return;
		adminApi
			.deleteIpActivity(target.id)
			.then(() => {
				setModal("");
				notify(`${target.ip} visit record deleted`);
				fetchRecords();
			})
			.catch(() => notify("Failed to delete visit record"));
	};
	const togglePolicy = (record: IpRecord) => {
		const policy = policyByIp.get(record.ip);
		const blocked = policy?.status === "blocked";
		const action = policy
			? adminApi.updateIpPolicy(policy.id, blocked ? "active" : "blocked")
			: adminApi.createIpPolicy(record.ip, "blocked");
		action
			.then(() => {
				notify(`${record.ip} ${blocked ? "unblocked" : "blocked"} successfully`);
				fetchRecords();
			})
			.catch(() => notify("Failed to update IP policy"));
	};
	const exportIps = () => {
		const csv = ["IP,Status,Device,OS,Browser,Page,Visits,Last Visited", ...filtered.map((item) => `${item.ip},${policyStatusName(statusOf(item.ip))},${item.device},${item.os},${item.browser},${item.page},${item.visits},${item.updatedAt}`)].join("\n");
		const link = document.createElement("a");
		link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
		link.download = "poojapoint-ip-addresses.csv";
		link.click();
		notify("Preparing IP address export...");
	};
	const totalVisits = records.reduce((sum, record) => sum + record.visits, 0);
	const uniqueIps = new Set(records.map((record) => record.ip)).size;
	const blockedCount = records.filter((record) => isBlocked(record.ip)).length;
	const today = records.filter((record) => new Date(record.createdAt).toDateString() === new Date().toDateString()).length;

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
								<div className="ip-exact-description">Monitor visitor traffic, devices, browsers and visited pages.</div>
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
								<button type="button" onClick={() => fetchRecords(true)}>
									<AdminIcon name="ip" />
									Refresh
								</button>
							</div>
						</div>
						<section className="ip-exact-summary">
							{[
								["ip", "TOTAL VISITS", String(totalVisits), "Visits recorded across all pages"],
								["customers", "UNIQUE IPS", String(uniqueIps), "Distinct visitor addresses"],
								["ban", "BLOCKED IPS", String(blockedCount), "Addresses blocked from the store"],
								["clock", "TRACKED TODAY", String(today), "Visitor records captured today"],
							].map(([icon, name, value, note]) => (
								<article key={name}>
									<div>
										<AdminIcon name={icon as "ip" | "customers" | "ban" | "clock"} />
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
									<input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search IP, device, browser, OS..." />
								</label>
								<select value={device} onChange={(event) => setDevice(event.target.value)}>
									<option value="all">All Devices</option>
									<option value="desktop">Desktop</option>
									<option value="mobile">Mobile</option>
									<option value="tablet">Tablet</option>
								</select>
								<select value={status} onChange={(event) => setStatus(event.target.value)}>
									<option value="all">All Status</option>
									<option value="open">Open</option>
									<option value="blocked">Blocked</option>
									<option value="active">Active</option>
									<option value="whitelisted">Whitelisted</option>
								</select>
								<span>Showing {filtered.length} records</span>
							</div>
							<div className="ip-exact-table-wrap">
								<table className="ip-exact-table">
									<thead>
										<tr>
											{["IP Address", "Device", "OS", "Browser", "Visited Page", "Visits", "Last Visited", "Actions"].map((heading) => (
												<th key={heading}>{heading}</th>
											))}
										</tr>
									</thead>
									<tbody>
										{filtered.map((record) => (
											<tr key={record.id}>
												<td>
													<strong>{record.ip}</strong>
													<small>{record.action}</small>
													<span className={`ip-exact-status ${statusOf(record.ip)}`}>{policyStatusName(statusOf(record.ip))}</span>
												</td>
												<td>
													<b>{record.device}</b>
													<small>{deviceTypeName(record.deviceType)}</small>
												</td>
												<td>{record.os}</td>
												<td>
													<b>{record.browser}</b>
												</td>
												<td>
													<b>{record.page}</b>
												</td>
												<td>
													<b>{record.visits}</b>
												</td>
												<td>{formatDate(record.updatedAt)}</td>
												<td>
													<div className="ip-exact-row-actions">
														<button type="button" aria-label={`${isBlocked(record.ip) ? "Unblock" : "Block"} ${record.ip}`} onClick={() => togglePolicy(record)}>
															<AdminIcon name={isBlocked(record.ip) ? "check" : "ban"} />
														</button>
														<button type="button" aria-label={`View ${record.ip}`} onClick={() => { setTarget(record); setModal("view"); }}>
															<AdminIcon name="eye" />
														</button>
														<button type="button" aria-label={`Edit ${record.ip}`} onClick={() => openEdit(record)}>
															<AdminIcon name="edit" />
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
								{!filtered.length && <div className="admin-empty-state">{loading ? "Loading IP addresses..." : "No IP visits match the selected filters."}</div>}
							</div>
							<div className="ip-exact-pagination">
								<span>Showing 1–{filtered.length} of {total || filtered.length} IP addresses</span>
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
								<p>Visitor, device and page information</p>
							</div>
							<button type="button" onClick={() => setModal("")}>
								<AdminIcon name="close" />
							</button>
						</div>
						<div className="ip-exact-modal-body">
							<div className="ip-exact-detail-grid">
								{[
									["IP Address", target.ip],
									["Policy", policyStatusName(statusOf(target.ip))],
									["Device", target.device],
									["Device Type", deviceTypeName(target.deviceType)],
									["OS", target.os],
									["Browser", target.browser],
									["Visited Page", target.page],
									["Visit Count", String(target.visits)],
									["Action", target.action],
									["First Visited", formatDate(target.createdAt)],
									["Last Visited", formatDate(target.updatedAt)],
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
							<button type="button" onClick={() => { const record = target; setModal(""); togglePolicy(record); }}>
								{isBlocked(target.ip) ? "Unblock IP" : "Block IP"}
							</button>
							<button className="primary" type="button" onClick={() => { setModal(""); openEdit(target); }}>
								Edit Record
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
								<h2>{editing ? "Edit Visit Record" : "Add IP Address"}</h2>
								<p>Create or update a visitor record</p>
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
										<label>
											Visited Page<span> *</span>
										</label>
										<input required type="text" value={form.page} onChange={(event) => setField("page", event.target.value)} placeholder="e.g. /shop" />
									</div>
									<div className="ip-exact-form-group">
										<label>Device</label>
										<input type="text" value={form.device} onChange={(event) => setField("device", event.target.value)} placeholder="e.g. Windows PC, iPhone" />
									</div>
									<div className="ip-exact-form-group">
										<label>Device Type</label>
										<select value={form.deviceType} onChange={(event) => setField("deviceType", event.target.value)}>
											<option value="desktop">Desktop</option>
											<option value="mobile">Mobile</option>
											<option value="tablet">Tablet</option>
											<option value="unknown">Unknown</option>
										</select>
									</div>
									<div className="ip-exact-form-group">
										<label>Operating System</label>
										<input type="text" value={form.os} onChange={(event) => setField("os", event.target.value)} placeholder="e.g. Windows, Android" />
									</div>
									<div className="ip-exact-form-group">
										<label>Browser</label>
										<input type="text" value={form.browser} onChange={(event) => setField("browser", event.target.value)} placeholder="e.g. Chrome, Firefox" />
									</div>
									<div className="ip-exact-form-group full">
										<label>Visit Count</label>
										<input type="number" min="1" value={form.visits} onChange={(event) => setField("visits", event.target.value)} placeholder="1" />
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
								<h2>Delete Visit Record?</h2>
							</div>
							<button type="button" onClick={() => setModal("")}>
								<AdminIcon name="close" />
							</button>
						</div>
						<div className="ip-exact-modal-body">
							<p className="ip-exact-delete-message">Deleting this visit record will remove it permanently from the tracked visitors list.</p>
							<div className="ip-exact-delete-name">{target.ip} · {target.page}</div>
						</div>
						<div className="ip-exact-modal-footer">
							<button type="button" onClick={() => setModal("")}>
								Cancel
							</button>
							<button className="danger" type="button" onClick={remove}>
								Delete Record
							</button>
						</div>
					</div>
				</div>
			)}
			{toast && <div className="coupon-exact-toast show">{toast}</div>}
		</div>
	);
}