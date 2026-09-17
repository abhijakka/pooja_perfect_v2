"use client";

import { useEffect, useRef } from "react";
import { getVisitorInfo } from "../lib/tracking";
import { trackVisit } from "../services/api/tracking.api";

/**
 * Tracks the current visitor's page view (IP, browser, device, OS) once per
 * mount. Mount this once near the app root so every visitor — logged in or
 * anonymous — is recorded.
 */
export function useVisitorTracking() {
	const sentRef = useRef(false);

	useEffect(() => {
		if (sentRef.current) return;
		sentRef.current = true;
		void trackVisit(getVisitorInfo("page_view"));
	}, []);
}