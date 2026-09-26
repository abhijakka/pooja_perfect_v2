// Google Identity Services (GIS) client loader.
//
// The backend already verifies the Google-signed `id_token` it receives, so the
// browser's only job is to obtain that token. GIS is loaded once per document
// from Google's own origin; no npm dependency is added and no OAuth state,
// client secret or profile data is handled here.

const GSI_SRC = "https://accounts.google.com/gsi/client";
const GSI_ID = "google-identity-services";

/** The subset of `google.accounts.id` this app uses, typed locally. */
export type GoogleCredentialResponse = {
	/** A Google-signed ID token. The only value ever sent to the backend. */
	credential?: string;
};

export type GooglePromptMomentNotification = {
	isNotDisplayed?: () => boolean;
	isSkippedMoment?: () => boolean;
	isDismissedMoment?: () => boolean;
	isDisabled?: () => boolean;
	getNotDisplayedReason?: () => string;
};

type GoogleIdApi = {
	initialize: (params: {
		client_id: string;
		callback: (response: GoogleCredentialResponse) => void;
		ux_mode?: "popup" | "redirect";
		use_fedcm_for_prompt?: boolean;
		auto_select?: boolean;
	}) => void;
	prompt: (notification?: (n: GooglePromptMomentNotification) => void) => void;
	cancel: () => void;
};

export type GoogleIdentity = { accounts: { id: GoogleIdApi } };

declare global {
	interface Window {
		google?: GoogleIdentity;
	}
}

let pending: Promise<GoogleIdentity> | null = null;

function existingGoogle(): GoogleIdentity | null {
	return typeof window === "undefined" ? null : (window.google ?? null);
}

/**
 * Load the GIS client once and resolve with `google.accounts.id`.
 *
 * Repeated and concurrent calls share the same in-flight promise, and a script
 * that is already on the page (or a `window.google` that arrived some other way)
 * is reused instead of being injected twice. Rejects when the script cannot be
 * loaded so callers can surface a real error rather than hanging.
 */
export function loadGoogleIdentity(): Promise<GoogleIdentity> {
	if (typeof window === "undefined") {
		return Promise.reject(new Error("Google sign in requires a browser"));
	}

	const ready = existingGoogle();
	if (ready?.accounts?.id) return Promise.resolve(ready);
	if (pending) return pending;

	pending = new Promise<GoogleIdentity>((resolve, reject) => {
		const finish = () => {
			const api = existingGoogle();
			if (api?.accounts?.id) {
				resolve(api);
			} else {
				// Allow a later attempt to retry instead of caching a broken promise.
				pending = null;
				reject(new Error("Google sign in is unavailable right now"));
			}
		};

		const existingScript = document.getElementById(GSI_ID) as HTMLScriptElement | null;
		if (existingScript) {
			existingScript.addEventListener("load", finish);
			existingScript.addEventListener("error", () => {
				pending = null;
				reject(new Error("Google sign in is unavailable right now"));
			});
			return;
		}

		const script = document.createElement("script");
		script.id = GSI_ID;
		script.src = GSI_SRC;
		script.async = true;
		script.defer = true;
		script.addEventListener("load", finish);
		script.addEventListener("error", () => {
			pending = null;
			reject(new Error("Google sign in is unavailable right now"));
		});
		document.head.appendChild(script);
	});

	return pending;
}
