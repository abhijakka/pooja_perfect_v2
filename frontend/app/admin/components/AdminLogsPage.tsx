"use client";

import { useMemo, useState } from "react";
import { AdminHeader } from "./AdminHeader";
import { AdminIcon, AdminIconSprite } from "./AdminIcon";
import { AdminSidebar } from "./AdminSidebar";

type LogLevel = "info" | "warning" | "error" | "security";
type LogRecord = { id: string; time: string; level: LogLevel; action: string; description: string; actor: string; source: string; ip: string; status: string };

const initialLogs: LogRecord[] = [
	{ id: "LOG-2846", time: "19 Aug 2026 · 14:32:08", level: "info", action: "Customer login", description: "Customer signed in successfully", actor: "Abhinav Kumar", source: "Authentication", ip: "103.84.121.44", status: "Success" },
	{ id: "LOG-2845", time: "19 Aug 2026 · 14:28:41", level: "security", action: "IP blocked", description: "Suspicious traffic was blocked automatically", actor: "Security service", source: "IP Protection", ip: "45.132.191.27", status: "Blocked" },
	{ id: "LOG-2844", time: "19 Aug 2026 · 14:18:26", level: "info", action: "Order created", description: "New order #PP102834 was placed", actor: "Sneha Reddy", source: "Orders", ip: "49.36.118.72", status: "Success" },
	{ id: "LOG-2843", time: "19 Aug 2026 · 13:58:12", level: "warning", action: "Failed payment", description: "Payment attempt was declined by the provider", actor: "Rahul Sharma", source: "Payments", ip: "117.198.42.91", status: "Warning" },
	{ id: "LOG-2842", time: "19 Aug 2026 · 13:44:09", level: "info", action: "Product updated", description: "Brass Diya Premium inventory was updated", actor: "PoojaPoint Admin", source: "Catalog", ip: "14.139.122.66", status: "Success" },
	{ id: "LOG-2841", time: "19 Aug 2026 · 13:26:54", level: "error", action: "API request failed", description: "Product service returned a 503 response", actor: "System", source: "API Gateway", ip: "127.0.0.1", status: "Failed" },
	{ id: "LOG-2840", time: "19 Aug 2026 · 12:46:17", level: "security", action: "Login attempt blocked", description: "Multiple failed attempts from an unknown visitor", actor: "Unknown Visitor", source: "Authentication", ip: "185.220.101.18", status: "Blocked" },
	{ id: "LOG-2839", time: "19 Aug 2026 · 12:15:03", level: "info", action: "Settings changed", description: "Notification preferences were updated", actor: "PoojaPoint Admin", source: "Settings", ip: "14.139.122.66", status: "Success" },
];

const levelName = (value: LogLevel) => value[0].toUpperCase() + value.slice(1);

export function AdminLogsPage() {
	const [sidebarOpen, setSidebarOpen] = useState(false);
	const [logs, setLogs] = useState<LogRecord[]>([]);
	const [query, setQuery] = useState("");
	const [level, setLevel] = useState("all");
	const [source, setSource] = useState("all");
	const [selected, setSelected] = useState<LogRecord | null>(null);
	const [toast, setToast] = useState("");
	const filtered = useMemo(() => logs.filter((log) => {
		const term = query.trim().toLowerCase();
		return (!term || `${log.id} ${log.action} ${log.description} ${log.actor} ${log.ip}`.toLowerCase().includes(term)) && (level === "all" || log.level === level) && (source === "all" || log.source === source);
	}), [logs, query, level, source]);
	const notify = (message: string) => { setToast(message); window.setTimeout(() => setToast(""), 2300); };
	const exportLogs = () => {
		const csv = ["ID,Time,Level,Action,Actor,Source,IP,Status", ...filtered.map((log) => [log.id, log.time, log.level, log.action, log.actor, log.source, log.ip, log.status].map((value) => `"${value.replaceAll('"', '""')}"`).join(","))].join("\n");
		const link = document.createElement("a");
		link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
		link.download = "poojapoint-activity-logs.csv";
		link.click();
		notify("Preparing activity log export...");
	};
	const clearLogs = () => { setLogs([]); notify("Activity logs cleared from this view"); };

	return <div className="admin-dashboard"><AdminIconSprite /><AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} activeHref="/admin/logs" /><main className="admin-main"><AdminHeader onMenu={() => setSidebarOpen(true)} query={query} onQuery={setQuery} title="Activity Logs" subtitle="Review security and operational events across your PoojaPoint store" /><div className="admin-content"><div className="logs-exact-page"><div className="logs-exact-top"><div><div className="logs-exact-heading">Activity Logs</div><div className="logs-exact-description">Track important actions, system events and security activity.</div></div><div className="logs-exact-actions"><button type="button" onClick={exportLogs}><AdminIcon name="download" />Export</button><button className="primary" type="button" onClick={() => notify("Activity logs refreshed")}><AdminIcon name="clock" />Refresh</button></div></div><section className="logs-exact-summary">{[["note", "TOTAL EVENTS", "2,846", "Recorded activity events"], ["check", "SUCCESSFUL", "2,712", "95.3% of all events"], ["alert", "WARNINGS", "86", "Events needing attention"], ["security", "SECURITY EVENTS", "48", "Blocked or restricted activity"]].map(([icon, name, value, note]) => <article key={name}><div><AdminIcon name={icon as "note" | "check" | "alert" | "security"} /></div><span>{name}</span><strong>{value}</strong><small>{note}</small></article>)}</section><section className="logs-exact-panel"><div className="logs-exact-toolbar"><label><AdminIcon name="search" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search events, actors, IP addresses..." /></label><select value={level} onChange={(event) => setLevel(event.target.value)}><option value="all">All Levels</option><option value="info">Info</option><option value="warning">Warning</option><option value="error">Error</option><option value="security">Security</option></select><select value={source} onChange={(event) => setSource(event.target.value)}><option value="all">All Sources</option>{[...new Set(logs.map((log) => log.source))].map((value) => <option value={value} key={value}>{value}</option>)}</select><button type="button" onClick={clearLogs}>Clear View</button><span>Showing {filtered.length} events</span></div><div className="logs-exact-table-wrap"><table className="logs-exact-table"><thead><tr>{["Event", "Level", "Activity", "Actor", "Source", "IP Address", "Status", "Actions"].map((heading) => <th key={heading}>{heading}</th>)}</tr></thead><tbody>{filtered.map((log) => <tr key={log.id}><td><strong>{log.id}</strong><small>{log.time}</small></td><td><span className={`logs-exact-level ${log.level}`}>{levelName(log.level)}</span></td><td><b>{log.action}</b><small>{log.description}</small></td><td>{log.actor}</td><td>{log.source}</td><td><strong>{log.ip}</strong></td><td><span className={`logs-exact-status ${log.status.toLowerCase()}`}>{log.status}</span></td><td><button className="logs-exact-view" type="button" aria-label={`View ${log.id}`} onClick={() => setSelected(log)}><AdminIcon name="eye" /></button></td></tr>)}</tbody></table>{!filtered.length && <div className="admin-empty-state">No activity logs match the selected filters.</div>}</div><div className="logs-exact-pagination"><span>Showing {filtered.length ? 1 : 0}–{filtered.length} of {filtered.length} events</span><div>{["‹", "1", "2", "3", "›"].map((value) => <button className={value === "1" ? "active" : ""} type="button" key={value}>{value}</button>)}</div></div></section></div></div></main>{selected && <div className="logs-exact-modal-overlay" role="presentation" onClick={(event) => event.target === event.currentTarget && setSelected(null)}><div className="logs-exact-modal"><div className="logs-exact-modal-header"><div><h2>Event Details</h2><p>{selected.id} · {selected.time}</p></div><button type="button" aria-label="Close event details" onClick={() => setSelected(null)}><AdminIcon name="close" /></button></div><div className="logs-exact-modal-body"><div className="logs-exact-detail-grid">{[["Event", selected.action], ["Level", levelName(selected.level)], ["Description", selected.description], ["Actor", selected.actor], ["Source", selected.source], ["IP Address", selected.ip], ["Status", selected.status]].map(([name, value]) => <div key={name}><span>{name}</span><strong>{value}</strong></div>)}</div></div><div className="logs-exact-modal-footer"><button type="button" onClick={() => setSelected(null)}>Close</button><button className="primary" type="button" onClick={() => notify("Event reference copied")}>Copy Reference</button></div></div></div>}{toast && <div className="coupon-exact-toast show">{toast}</div>}</div>;
}
