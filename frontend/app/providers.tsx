"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Provider } from "react-redux";
import { authApi } from "../services/api/auth.api";
import { ApiError, setUnauthorizedHandler } from "../services/api/client";
import { cartApi } from "../services/api/cart.api";
import { makeStore } from "../store";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { logout, setAuthReady, setSessionExpired, setTokenExpiry, setUser } from "../store/slices/authSlice";
import { hydrate as hydrateCart } from "../store/slices/cartSlice";
import { hydrate as hydrateWishlist } from "../store/slices/wishlistSlice";
import { setOnline } from "../store/slices/connectionSlice";
import { SupportChat } from "../components/chat/SupportChat";
import { useVisitorTracking } from "../hooks/useVisitorTracking";

/** Pages where a missing/invalid access token is expected — never redirect those to home. */
const AUTH_PAGES = ["/login", "/signup", "/register", "/forgot-password", "/reset-password", "/otp", "/two-factor"];

function isAuthPage(): boolean {
	return AUTH_PAGES.some((page) => window.location.pathname.startsWith(page));
}

function AuthBootstrap({ children }: Readonly<{ children: React.ReactNode }>) {
	const dispatch = useAppDispatch();
	const router = useRouter();
	const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);
	const accessTokenExpiresAt = useAppSelector((state) => state.auth.accessTokenExpiresAt);

	const endSession = useCallback(() => {
		dispatch(setSessionExpired());
		dispatch(logout());
		if (!isAuthPage()) router.replace("/");
	}, [dispatch, router]);

	useEffect(() => {
		setUnauthorizedHandler(endSession);
		return () => setUnauthorizedHandler(undefined);
	}, [endSession]);

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
				dispatch(setSessionExpired());
				dispatch(logout());
				if (error instanceof ApiError && error.status === 401 && !isAuthPage()) {
					router.replace("/");
				}
			}
		};
		restoreSession().finally(() => {
			if (isMounted) dispatch(setAuthReady());
		});
		return () => {
			isMounted = false;
		};
	}, [dispatch, router]);

	useEffect(() => {
		if (!isAuthenticated || accessTokenExpiresAt == null) return;
		const interval = window.setInterval(() => {
			if (Date.now() >= accessTokenExpiresAt) {
				endSession();
			}
		}, 1000);
		return () => window.clearInterval(interval);
	}, [endSession, isAuthenticated, accessTokenExpiresAt]);

	return children;
}

export default function Providers({ children }: Readonly<{ children: React.ReactNode }>) {
	const [store] = useState(makeStore);
	useVisitorTracking();
	useEffect(() => {
		try {
			const savedWishlist = window.localStorage.getItem("poojapoint-wishlist");
			if (savedWishlist) store.dispatch(hydrateWishlist(JSON.parse(savedWishlist)));
			const savedCart = window.localStorage.getItem("poojapoint-cart");
			if (savedCart) store.dispatch(hydrateCart(JSON.parse(savedCart)));
		} catch {}

		let isActive = true;
		cartApi.get().then(({ cart }) => {
			if (!isActive) return;
			const items = (cart?.items ?? []).map((item) => ({
				id: item.productId ?? item.id,
				name: item.product?.name ?? item.id,
				price: Number(item.unitPrice ?? item.product?.price ?? 0),
				oldPrice: Number(item.product?.price ?? item.unitPrice ?? 0),
				rating: "5.0",
				category: "pooja",
				categoryLabel: "Pooja Essentials",
				slug: item.product?.slug ?? item.id,
				image: item.product?.images?.find((image) => image.isPrimary)?.url ?? item.product?.images?.[0]?.url ?? "",
				quantity: item.quantity,
			}));
			store.dispatch(hydrateCart(items));
			store.dispatch(setOnline(true));
		}).catch(() => {
			if (!isActive) return;
			store.dispatch(setOnline(false));
		});

		return () => {
			isActive = false;
		};
	}, [store]);
	return (
		<Provider store={store}>
			<AuthBootstrap>{children}</AuthBootstrap>
			<SupportChat />
		</Provider>
	);
}
