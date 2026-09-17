import { environment } from "../../config/environment";
import type { VisitorInfo } from "../../lib/tracking";

/**
 * Fire-and-forget visitor tracking beacon.
 *
 * Uses `navigator.sendBeacon` when available (survives page unload) and falls
 * back to a plain `fetch` with `keepalive`. Never throws — tracking must never
 * break the page.
 */
export async function trackVisit(info: VisitorInfo): Promise<void> {
	try {
		const baseUrl = environment.apiUrl.replace(/\/+$/, "");
		const url = `${baseUrl}/api/track`;
		const body = JSON.stringify(info);

		if (typeof navigator !== "undefined" && typeof navigator.sendBeacon === "function") {
			const blob = new Blob([body], { type: "application/json" });
			navigator.sendBeacon(url, blob);
			return;
		}

		await fetch(url, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body,
			credentials: "include",
			keepalive: true,
		});
	} catch {
		// Tracking is best-effort; ignore failures silently.
	}
}