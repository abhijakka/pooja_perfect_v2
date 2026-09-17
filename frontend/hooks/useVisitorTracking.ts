"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import { getVisitorInfo } from "../lib/tracking";
import { trackVisit } from "../services/api/tracking.api";

/**
 * Tracks the current visitor's page view (IP, browser, device, OS) on every
 * route change. Mount this once near the app root so every visitor — logged
 * in or anonymous — is recorded for each page they visit. A dedupe ref
 * guarantees exactly one beacon per pathname, which also keeps it safe under
 * React Strict Mode.
 */
export function useVisitorTracking() {
	const pathname = usePathname() ?? "/";
	const lastPathRef = useRef<string | null>(null);

	useEffect(() => {
		if (lastPathRef.current === pathname) return;
		lastPathRef.current = pathname;
		void trackVisit(getVisitorInfo("page_view"));
	}, [pathname]);
}