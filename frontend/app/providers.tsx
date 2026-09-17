"use client";

import { useEffect, useState } from "react";
import { Provider } from "react-redux";
import { authApi } from "../services/api/auth.api";
import { cartApi } from "../services/api/cart.api";
import { makeStore } from "../store";
import { useAppDispatch } from "../store/hooks";
import { logout, setAuthReady, setUser } from "../store/slices/authSlice";
import { hydrate as hydrateCart } from "../store/slices/cartSlice";
import { hydrate as hydrateWishlist } from "../store/slices/wishlistSlice";
import { setOnline } from "../store/slices/connectionSlice";
import { SupportChat } from "../components/chat/SupportChat";
import { useVisitorTracking } from "../hooks/useVisitorTracking";

function AuthBootstrap({ children }: Readonly<{ children: React.ReactNode }>) {
	const dispatch = useAppDispatch();
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
			} catch {
				if (isMounted) dispatch(logout());
			}
		};
			restoreSession().finally(() => {
				if (isMounted) dispatch(setAuthReady());
			});
		return () => {
			isMounted = false;
		};
	}, [dispatch]);

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
