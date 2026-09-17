"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AdminHeader } from "./AdminHeader";
import { AdminIcon, AdminIconSprite } from "./AdminIcon";
import { AdminSidebar } from "./AdminSidebar";
import { adminApi, type AdminActivityLog } from "../../../services/api/admin.api";

type LogLevel = "info" | "warning" | "error" | "security";
type LogRecord = { id: string; time: string; level: LogLevel; action: string; description: string; actor: string; source: string; ip: string; status: string; method: string; path: string; statusCode: number | null };

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const pad = (value: number) => String(value).padStart(2, "0");
const LEVELS: LogLevel[] = ["info", "warning", "error", "security"];
const STATUS_BY_LEVEL: Record<LogLevel, string> = { info: "Success", warning: "Warning", error: "Failed", security: "Blocked" };

const formatTime = (value?: string | null) => {
	const date = value ? new Date(value) : new Date();
	if (Number.isNaN(date.getTime())) return "—";
	return `${pad(date.getDate())} ${MONTHS[date.getMonth()]} ${date.getFullYear()} · ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
};

const toLogRecord = (item: AdminActivityLog): LogRecord => {
	const value = (item.level || "info").toLowerCase();
	const level: LogLevel = (LEVELS as string[]).includes(value) ? (value as LogLevel) : "info";
	const actor = item.user ? item.user[0].toUpperCase() + item.user.slice(1) : "Guest";
	return {
		id: item.id,
		time: formatTime(item.createdAt),
		level,
		action: item.action || "Activity",
		description: item.details ?? item.action ?? "",
		actor,
		source: item.source ?? "API",
		ip: item.ipAddress ?? "unknown",
		status: item.status ?? STATUS_BY_LEVEL[level],
		method: item.method ?? "",
		path: item.path ?? "",
		statusCode: item.statusCode ?? null,
	};
};

const levelName = (value: LogLevel) => value[0].toUpperCase() + value.slice(1);

export function AdminLogsPage() {
	const [sidebarOpen, setSidebarOpen] = useState(false);
	const [logs, setLogs] = useState<LogRecord[]>([]);
	const [query, setQuery] = useState("");
	const [level, setLevel] = useState("all");
	const [source, setSource] = useState("all");
	const [selected, setSelected] = useState<LogRecord | null>(null);
	const [toast, setToast] = useState("");

	const fetchLogs = useCallback(() => {
		adminApi
			.listActivityLogs({ page: 1, pageSize: 100 })
			.then(({ activityLogs }) => setLogs(activityLogs.items.map(toLogRecord)))
			.catch(() => {
				setLogs([]);
				setToast("Failed to load activity logs");
				window.setTimeout(() => setToast(""), 2300);
			});
	}, []);

	useEffect(() => {
		fetchLogs();
	}, [fetchLogs]);

	const filtered = useMemo(() => logs.filter((log) => {
		const term = query.trim().toLowerCase();
		return (!term || `${log.id} ${log.action} ${log.description} ${log.actor} ${log.ip} ${log.method} ${log.path}`.toLowerCase().includes(term)) && (level === "all" || log.level === level) && (source === "all" || log.source === source);
	}), [logs, query, level, source]);
	const summary = useMemo(() => {
		const total = logs.length;
		const successful = logs.filter((log) => log.level === "info").length;
		const warnings = logs.filter((log) => log.level === "warning").length;
		const security = logs.filter((log) => log.level === "security").length;
		return [
			["note", "TOTAL EVENTS", String(total), "Recorded activity events"],
			["check", "SUCCESSFUL", String(successful), total ? `${Math.round((successful / total) * 100)}% of all events` : "No events recorded yet"],
			["alert", "WARNINGS", String(warnings), "Events needing attention"],
			["security", "SECURITY EVENTS", String(security), "Blocked or restricted activity"],
		] as const;
	}, [logs]);
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

	return <div className="admin-dashboard"><AdminIconSprite /><AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} activeHref="/admin/logs" /><main className="admin-main"><AdminHeader onMenu={() => setSidebarOpen(true)} query={query} onQuery={setQuery} title="Activity Logs" subtitle="Review security and operational events across your PoojaPoint store" /><div className="admin-content"><div className="logs-exact-page"><div className="logs-exact-top"><div><div className="logs-exact-heading">Activity Logs</div><div className="logs-exact-description">Track important actions, system events and security activity.</div></div><div className="logs-exact-actions"><button type="button" onClick={exportLogs}><AdminIcon name="download" />Export</button><button className="primary" type="button" onClick={() => { fetchLogs(); notify("Activity logs refreshed"); }}><AdminIcon name="clock" />Refresh</button></div></div><section className="logs-exact-summary">{summary.map(([icon, name, value, note]) => <article key={name}><div><AdminIcon name={icon as "note" | "check" | "alert" | "security"} /></div><span>{name}</span><strong>{value}</strong><small>{note}</small></article>)}</section><section className="logs-exact-panel"><div className="logs-exact-toolbar"><label><AdminIcon name="search" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search events, actors, IP addresses..." /></label><select value={level} onChange={(event) => setLevel(event.target.value)}><option value="all">All Levels</option><option value="info">Success</option><option value="warning">Warning</option><option value="error">Error</option><option value="security">Security</option></select><select value={source} onChange={(event) => setSource(event.target.value)}><option value="all">All Sources</option>{[...new Set(logs.map((log) => log.source))].map((value) => <option value={value} key={value}>{value}</option>)}</select><button type="button" onClick={clearLogs}>Clear View</button><span>Showing {filtered.length} events</span></div><div className="logs-exact-table-wrap"><table className="logs-exact-table"><thead><tr>{["Event", "Level", "Activity", "Actor", "Source", "IP Address", "Status", "Actions"].map((heading) => <th key={heading}>{heading}</th>)}</tr></thead><tbody>{filtered.map((log) => <tr key={log.id}><td><strong>{log.id}</strong><small>{log.time}</small></td><td><span className={`logs-exact-level ${log.level}`}>{levelName(log.level)}</span></td><td><b>{log.action}</b><small>{log.description}</small>{(log.method || log.path) && <small>{[[log.method, log.path].filter(Boolean).join(" "), log.statusCode ? `· ${log.statusCode}` : ""].filter(Boolean).join(" ")}</small>}</td><td>{log.actor}</td><td>{log.source}</td><td><strong>{log.ip}</strong></td><td><span className={`logs-exact-status ${log.status.toLowerCase()}`}>{log.status}</span></td><td><button className="logs-exact-view" type="button" aria-label={`View ${log.id}`} onClick={() => setSelected(log)}><AdminIcon name="eye" /></button></td></tr>)}</tbody></table>{!filtered.length && <div className="admin-empty-state">No activity logs match the selected filters.</div>}</div><div className="logs-exact-pagination"><span>Showing {filtered.length ? 1 : 0}–{filtered.length} of {filtered.length} events</span><div>{["‹", "1", "2", "3", "›"].map((value) => <button className={value === "1" ? "active" : ""} type="button" key={value}>{value}</button>)}</div></div></section></div></div></main>{selected && <div className="logs-exact-modal-overlay" role="presentation" onClick={(event) => event.target === event.currentTarget && setSelected(null)}><div className="logs-exact-modal"><div className="logs-exact-modal-header"><div><h2>Event Details</h2><p>{selected.id} · {selected.time}</p></div><button type="button" aria-label="Close event details" onClick={() => setSelected(null)}><AdminIcon name="close" /></button></div><div className="logs-exact-modal-body"><div className="logs-exact-detail-grid">{[["Event", selected.action], ["Level", levelName(selected.level)], ["Description", selected.description], ["Actor", selected.actor], ["Source", selected.source], ["IP Address", selected.ip], ["Status", selected.status], ["Method", selected.method || "—"], ["Path", selected.path || "—"], ["Status Code", selected.statusCode != null ? String(selected.statusCode) : "—"]].map(([name, value]) => <div key={name}><span>{name}</span><strong>{value}</strong></div>)}</div></div><div className="logs-exact-modal-footer"><button type="button" onClick={() => setSelected(null)}>Close</button><button className="primary" type="button" onClick={() => notify("Event reference copied")}>Copy Reference</button></div></div></div>}{toast && <div className="coupon-exact-toast show">{toast}</div>}</div>;
}
