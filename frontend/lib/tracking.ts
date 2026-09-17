/**
 * Client-side browser / OS / device detection.
 *
 * The backend also parses the User-Agent header, but the client can detect
 * extra signals (screen size, touch support, device type) that the server
 * cannot see. These are merged into the tracking beacon payload.
 */

export type VisitorInfo = {
	action: string;
	path: string;
	referrer: string | null;
	screen: string;
	browser: string;
	browserVersion: string;
	os: string;
	osVersion: string;
	device: string;
	deviceType: "mobile" | "tablet" | "desktop" | "unknown";
	isMobile: boolean;
};

function detectBrowser(ua: string): { browser: string; version: string } {
	if (/Edg\//.test(ua)) return { browser: "Edge", version: ua.match(/Edg\/([\d.]+)/)?.[1] ?? "" };
	if (/OPR\//.test(ua)) return { browser: "Opera", version: ua.match(/OPR\/([\d.]+)/)?.[1] ?? "" };
	if (/SamsungBrowser/.test(ua)) return { browser: "Samsung Internet", version: ua.match(/SamsungBrowser\/([\d.]+)/)?.[1] ?? "" };
	if (/Chrome\//.test(ua)) return { browser: "Chrome", version: ua.match(/Chrome\/([\d.]+)/)?.[1] ?? "" };
	if (/Firefox\//.test(ua)) return { browser: "Firefox", version: ua.match(/Firefox\/([\d.]+)/)?.[1] ?? "" };
	if (/Safari\//.test(ua)) return { browser: "Safari", version: ua.match(/Version\/([\d.]+)/)?.[1] ?? "" };
	if (/MSIE|Trident/.test(ua)) return { browser: "Internet Explorer", version: ua.match(/MSIE ([\d.]+)/)?.[1] ?? "" };
	return { browser: "Unknown", version: "" };
}

function detectOs(ua: string): { os: string; version: string } {
	if (/Windows NT 10\.0/.test(ua)) return { os: "Windows", version: "10" };
	if (/Windows NT 6\.3/.test(ua)) return { os: "Windows", version: "8.1" };
	if (/Windows NT 6\.2/.test(ua)) return { os: "Windows", version: "8" };
	if (/Windows NT 6\.1/.test(ua)) return { os: "Windows", version: "7" };
	if (/Windows Phone/.test(ua)) return { os: "Windows Phone", version: "" };
	if (/Android/.test(ua)) return { os: "Android", version: ua.match(/Android ([\d.]+)/)?.[1] ?? "" };
	if (/iPhone|iPad|iPod/.test(ua)) return { os: "iOS", version: ua.match(/OS ([\d_]+)/)?.[1]?.replace(/_/g, ".") ?? "" };
	if (/Mac OS X/.test(ua)) return { os: "macOS", version: ua.match(/Mac OS X ([\d_.]+)/)?.[1]?.replace(/_/g, ".") ?? "" };
	if (/CrOS/.test(ua)) return { os: "Chrome OS", version: "" };
	if (/Linux/.test(ua)) return { os: "Linux", version: "" };
	return { os: "Unknown", version: "" };
}

function detectDevice(ua: string, isMobile: boolean): { device: string; deviceType: VisitorInfo["deviceType"] } {
	if (/iPad/.test(ua)) return { device: "iPad", deviceType: "tablet" };
	if (/iPhone/.test(ua)) return { device: "iPhone", deviceType: "mobile" };
	if (/Android/.test(ua)) return { device: isMobile ? "Android Phone" : "Android Tablet", deviceType: isMobile ? "mobile" : "tablet" };
	if (/Windows Phone/.test(ua)) return { device: "Windows Phone", deviceType: "mobile" };
	if (/Macintosh|Mac/.test(ua)) return { device: "Mac", deviceType: "desktop" };
	if (/Windows/.test(ua)) return { device: "Windows PC", deviceType: "desktop" };
	if (/CrOS/.test(ua)) return { device: "Chromebook", deviceType: "desktop" };
	if (/Linux/.test(ua)) return { device: "Linux PC", deviceType: "desktop" };
	return { device: "Unknown", deviceType: "unknown" };
}

export function getVisitorInfo(action = "page_view"): VisitorInfo {
	if (typeof window === "undefined") {
		return {
			action,
			path: "/",
			referrer: null,
			screen: "",
			browser: "Unknown",
			browserVersion: "",
			os: "Unknown",
			osVersion: "",
			device: "Unknown",
			deviceType: "unknown",
			isMobile: false,
		};
	}

	const ua = navigator.userAgent;
	const isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(ua);
	const { browser, version: browserVersion } = detectBrowser(ua);
	const { os, version: osVersion } = detectOs(ua);
	const { device, deviceType } = detectDevice(ua, isMobile);

	return {
		action,
		path: window.location.pathname + window.location.search,
		referrer: document.referrer || null,
		screen: `${window.screen?.width ?? 0}x${window.screen?.height ?? 0}`,
		browser,
		browserVersion,
		os,
		osVersion,
		device,
		deviceType,
		isMobile,
	};
}