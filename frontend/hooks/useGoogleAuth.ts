"use client";

import { useCallback, useRef, useState } from "react";
import { authApi } from "../services/api/auth.api";
import { loadGoogleIdentity } from "../services/google/google-identity";
import type { GooglePromptMomentNotification } from "../services/google/google-identity";
import type { UserResponse } from "../types/auth";
import { useAppDispatch } from "../store/hooks";
import { setTokenExpiry, setUser } from "../store/slices/authSlice";

/**
 * Backstop so an attempt can never leave the button spinning forever. Google's
 * own moment notification settles every known outcome; this only covers the
 * case where the browser reports nothing at all.
 */
const ATTEMPT_TIMEOUT_MS = 5 * 60 * 1000;

/**
 * FedCM closes its account chooser the moment the user picks an account, and
 * Google reports that close as a *dismissed* moment — the credential callback
 * then arrives a tick later. A dismissal is therefore ambiguous: it means
 * "cancelled" only when no credential follows. Wait this long for the
 * credential before telling the user the attempt was cancelled, otherwise a
 * successful sign-in is reported as a cancellation and never redirects.
 */
const DISMISSAL_GRACE_MS = 3000;

const ERRORS = {
	unavailable: "Google sign in is unavailable. Please try again or use email and password.",
	disabled: "Google sign in is turned off for this browser.",
	cancelled: "Google sign in was cancelled.",
	rejected: "Google sign in could not be completed. Please try again.",
	notConfigured: "Google sign in is not configured yet.",
} as const;

type Options = {
	/** Called with a user-facing message for every failure path. */
	onError?: (message: string) => void;
};

/**
 * Shared "Continue with Google" flow for the login and register pages.
 *
 * Deliberately mirrors the password path in `app/(auth)/login/page.tsx` step for
 * step — obtain a Google-signed `id_token`, post it to the existing
 * `POST /auth/google`, then run the same `setTokenExpiry` → `me()` → `setUser`
 * sequence. The backend sets the normal HttpOnly cookies, so a Google sign-in
 * ends in exactly the same application session as a password sign-in. The
 * token is discarded once the request completes; no Google-only session exists.
 *
 * Only the `id_token` is read from Google's response. No name, email or any
 * other profile value from the browser is trusted or forwarded — the backend
 * re-verifies the token and derives every field from verified claims.
 *
 * Resolves with the authenticated user, or `null` when the attempt failed, so
 * the caller keeps ownership of its own success copy and role redirect.
 */
export function useGoogleAuth({ onError }: Options = {}) {
	const dispatch = useAppDispatch();
	const [isBusy, setIsBusy] = useState(false);
	const busyRef = useRef(false);

	const fail = useCallback(
		(message: string) => {
			busyRef.current = false;
			setIsBusy(false);
			onError?.(message);
		},
		[onError],
	);

	const signInWithGoogle = useCallback(async (): Promise<UserResponse | null> => {
		if (busyRef.current) return null; // an attempt is already in flight
		busyRef.current = true;
		setIsBusy(true);

		const bail = async (message: string) => {
			fail(message);
			return null;
		};

		let clientId: string;
		try {
			({ client_id: clientId } = await authApi.googleConfig());
		} catch {
			return bail(ERRORS.unavailable);
		}
		if (!clientId) return bail(ERRORS.notConfigured);

		let id;
		try {
			id = await loadGoogleIdentity();
		} catch {
			return bail(ERRORS.unavailable);
		}

		return new Promise<UserResponse | null>((resolve) => {
			let settled = false;
			let retried = false;
			let timer = 0;
			let dismissalTimer = 0;

			const settle = (user: UserResponse | null, message?: string) => {
				if (settled) return;
				settled = true;
				window.clearTimeout(timer);
				window.clearTimeout(dismissalTimer);
				if (user) {
					busyRef.current = false;
					setIsBusy(false);
				} else {
					fail(message ?? ERRORS.rejected);
				}
				resolve(user);
			};

			timer = window.setTimeout(() => settle(null, ERRORS.cancelled), ATTEMPT_TIMEOUT_MS);

			// Google's moment notification drives the retry and terminal decisions
			// so the button never stays spinning and the user is never redirected
			// on a failed attempt. A dismissed moment is the one outcome that is
			// not yet terminal, so it only starts a grace timer — FedCM emits it
			// for a completed selection too, and failing on it would discard a
			// credential that is already on its way.
			const onMoment = (n: GooglePromptMomentNotification) => {
				if (settled) return;
				if (n.isDisabled?.()) return settle(null, ERRORS.disabled);
				const skippable = Boolean(n.isSkippedMoment?.() || n.isNotDisplayed?.());
				// One silent retry, per Google's guidance for a skipped moment.
				if (skippable && !retried) {
					retried = true;
					id.accounts.id.prompt(onMoment);
					return;
				}
				if (skippable) return settle(null, ERRORS.unavailable);
				window.clearTimeout(dismissalTimer);
				dismissalTimer = window.setTimeout(() => settle(null, ERRORS.cancelled), DISMISSAL_GRACE_MS);
			};

			id.accounts.id.initialize({
				client_id: clientId,
				ux_mode: "popup",
				use_fedcm_for_prompt: true,
				callback: (response) => {
					const idToken = response?.credential;
					if (!idToken) {
						settle(null, ERRORS.rejected);
						return;
					}
					authApi
						.googleLogin({ provider: "google", id_token: idToken })
						.then(async (tokens) => {
							if (tokens.expires_at) dispatch(setTokenExpiry(Date.parse(tokens.expires_at)));
							const me = await authApi.me();
							dispatch(
								setUser({
									id: me.id,
									name: `${me.first_name} ${me.last_name}`.trim(),
									email: me.email,
									role_name: me.role_name,
								}),
							);
							settle(me);
						})
						.catch(() => settle(null, ERRORS.rejected));
				},
			});

			id.accounts.id.prompt(onMoment);
		});
	}, [dispatch, fail]);

	return { isBusy, signInWithGoogle };
}
