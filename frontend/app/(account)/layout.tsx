"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../hooks/useAuth";

export default function AccountLayout({ children }: Readonly<{ children: React.ReactNode }>) {
	const router = useRouter();
	const { user, isAuthenticated, isReady } = useAuth();
	useEffect(() => {
		if (!isReady) return;
		if (!isAuthenticated || user?.role_name !== "customer") router.replace(user?.role_name === "admin" ? "/admin" : "/login");
	}, [isAuthenticated, isReady, router, user?.role_name]);
	if (!isReady || !isAuthenticated || user?.role_name !== "customer") return null;
	return children;
}