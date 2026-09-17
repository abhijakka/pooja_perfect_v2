"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../hooks/useAuth";
import "./styles/admin_style.css";

export default function AdminLayout({ children }: Readonly<{ children: React.ReactNode }>) {
	const router = useRouter();
	const { user, isAuthenticated, isReady } = useAuth();
	useEffect(() => {
		if (!isReady) return;
		if (!isAuthenticated || user?.role_name !== "admin") router.replace(isAuthenticated ? "/" : "/login");
	}, [isAuthenticated, isReady, router, user?.role_name]);
	if (!isReady || !isAuthenticated || user?.role_name !== "admin") return null;
	return <div className="admin-shell">{children}</div>;
}
