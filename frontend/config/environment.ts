export function resolveApiUrl(hostname?: string, protocol?: string): string {
	const configured = process.env.NEXT_PUBLIC_API_URL;
	if (configured) return configured;

	const host = hostname ?? (typeof window !== "undefined" ? window.location.hostname : undefined);
	const proto = protocol ?? (typeof window !== "undefined" ? window.location.protocol : undefined);

	// On a phone (or any device on the LAN) the page is served from the PC's
	// LAN IP (e.g. http://192.168.1.34:3000). "localhost" would point at the
	// device itself, so derive the API host from the page's own host instead.
	if (host && host !== "localhost" && host !== "127.0.0.1") {
		return `${proto ?? "http:"}//${host}:8000`;
	}
	return "http://localhost:8000";
}

export const environment = {
	apiUrl: resolveApiUrl(),
};
