"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Provider } from "react-redux";
import { authApi } from "../services/api/auth.api";
import { ApiError, setSessionRefresher, setUnauthorizedHandler } from "../services/api/client";
import { cartApi, toCartItems } from "../services/api/cart.api";
import { makeStore } from "../store";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { logout, setAuthReady, setSessionExpired, setTokenExpiry, setUser } from "../store/slices/authSlice";
import { hydrate as hydrateCart } from "../store/slices/cartSlice";
import { hydrate as hydrateWishlist } from "../store/slices/wishlistSlice";
import { setOnline } from "../store/slices/connectionSlice";
import { SupportChat } from "../components/chat/SupportChat";
import { ChatProvider } from "../context/ChatContext";
import { useVisitorTracking } from "../hooks/useVisitorTracking";

/** Pages where a missing/invalid access token is expected — never redirect those to home. */
const AUTH_PAGES = ["/login", "/signup", "/register", "/forgot-password", "/reset-password", "/otp", "/two-factor"];

/** Renew a little before the access token dies so in-flight work is never interrupted. */
const REFRESH_LEEWAY_MS = 60_000;

function isAuthPage(): boolean {
	return AUTH_PAGES.some((page) => window.location.pathname.startsWith(page));
}

function AuthBootstrap({ children }: Readonly<{ children: React.ReactNode }>) {
	const dispatch = useAppDispatch();
	const router = useRouter();
	const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);
	const accessTokenExpiresAt = useAppSelector((state) => state.auth.accessTokenExpiresAt);

	/**
	 * Exchange the HttpOnly refresh_token cookie for a new access token. This is the single
	 * recovery path: both the expiry timer and the API client's 401 handling call it, and
	 * the API client de-duplicates concurrent calls. Resolves false only when the session
	 * is genuinely unrecoverable.
	 */
	const refreshAccessToken = useCallback(async () => {
		try {
			const tokens = await authApi.refresh();
			if (tokens.expires_at) dispatch(setTokenExpiry(Date.parse(tokens.expires_at)));
			return true;
		} catch {
			return false;
		}
	}, [dispatch]);

	// Ending a session that does not exist would bounce anonymous visitors off public pages,
	// so this only acts on a real, unrecovered session.
	const endSession = useCallback(() => {
		if (!isAuthenticated) return;
		dispatch(setSessionExpired());
		dispatch(logout());
		if (!isAuthPage()) router.replace("/");
	}, [dispatch, isAuthenticated, router]);

	useEffect(() => {
		setUnauthorizedHandler(endSession);
		return () => setUnauthorizedHandler(undefined);
	}, [endSession]);

	useEffect(() => {
		setSessionRefresher(refreshAccessToken);
		return () => setSessionRefresher(undefined);
	}, [refreshAccessToken]);

	useEffect(() => {
		let isMounted = true;
		const restoreSession = async () => {
			try {
				const me = await authApi.me();
				if (!isMounted) return;
				dispatch(
					setUser({
						id: me.id,
						name: `${me.first_name} ${me.last_name}`.trim(),
						email: me.email,
						role_name: me.role_name,
					}),
				);
				if (me.expires_at) dispatch(setTokenExpiry(Date.parse(me.expires_at)));
			} catch (error) {
				if (!isMounted) return;
				// The API client already spent a refresh attempt on this 401 and only rethrows
				// when the session is unrecoverable, so a 401 here means there is no session to
				// end. Calling endSession() (rather than logging out directly) keeps this a
				// no-op for anonymous visitors on public direct URLs.
				if (error instanceof ApiError && error.status === 401) {
					endSession();
					return;
				}
				// A network or server failure says nothing about the session, so leave it alone.
			}
		};
		restoreSession().finally(() => {
			if (isMounted) dispatch(setAuthReady());
		});
		return () => {
			isMounted = false;
		};
	}, [dispatch, endSession]);

	// Renew ahead of expiry instead of ending the session. The previous 1 s polling loop
	// logged the user out at access_token_expire_minutes even though a valid 30-day
	// refresh_token cookie was still in the browser.
	useEffect(() => {
		if (!isAuthenticated || accessTokenExpiresAt == null) return;
		const wait = Math.min(Math.max(accessTokenExpiresAt - REFRESH_LEEWAY_MS - Date.now(), 0), 2_147_000_000);
		const timer = window.setTimeout(() => {
			void refreshAccessToken().then((recovered) => {
				if (!recovered) endSession();
			});
		}, wait);
		return () => window.clearTimeout(timer);
	}, [accessTokenExpiresAt, endSession, isAuthenticated, refreshAccessToken]);

	return children;
}

/**
 * Wishlist and cart bootstrap.
 *
 * This must be a child of <Provider>: `useAppSelector`/`useAppDispatch` resolve the store
 * from React context, and `Providers` renders the <Provider> itself, so a hook in
 * `Providers` would run with no store in context and react-redux v9 throws
 * ("could not find react-redux context value").
 */
function StoreBootstrap() {
	const dispatch = useAppDispatch();
	// The backend cart is the only cart. It is identified by the guest_token cookie for
	// anonymous visitors and by the customer id once authenticated, so it stays stable across
	// navigation, refresh and sign-in. It is re-read when the session settles so a guest who
	// signs in sees the cart the backend resolves for that identity.
	const authReady = useAppSelector((state) => state.auth.isReady);
	const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);

	// Wishlist is a purely local mirror of a public list, so it is restored once per load.
	useEffect(() => {
		try {
			const savedWishlist = window.localStorage.getItem("poojapoint-wishlist");
			if (savedWishlist) dispatch(hydrateWishlist(JSON.parse(savedWishlist)));
		} catch {
			// A malformed or unreadable mirror must not stop the app from starting.
		}
	}, [dispatch]);

	useEffect(() => {
		// `authReady` flips once, when /auth/me settles. React runs this effect's cleanup
		// before the next one, so the `isActive` flag already guarantees a superseded
		// response can never overwrite a newer read — no extra revision counter is needed.
		//
		// `isAuthenticated` is a dependency in its own right: a client-side sign-in or
		// sign-out never re-flips `authReady`, and the backend resolves a different cart for
		// a customer than for the guest token, so the store must be re-read on that
		// transition too.
		let isActive = true;
		cartApi.get().then(({ cart }) => {
			if (!isActive) return;
			dispatch(hydrateCart(toCartItems(cart)));
			dispatch(setOnline(true));
		}).catch(() => {
			if (!isActive) return;
			dispatch(setOnline(false));
		});

		return () => {
			isActive = false;
		};
	}, [authReady, isAuthenticated, dispatch]);

	return null;
}

export default function Providers({ children }: Readonly<{ children: React.ReactNode }>) {
	const [store] = useState(makeStore);
	useVisitorTracking();

	return (
		<Provider store={store}>
			<StoreBootstrap />
			<ChatProvider>
				<AuthBootstrap>{children}</AuthBootstrap>
				<SupportChat />
			</ChatProvider>
		</Provider>
	);
}
