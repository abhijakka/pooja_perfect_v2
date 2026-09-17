import React from "react";
import { render, renderHook, type RenderOptions } from "@testing-library/react";
import { Provider } from "react-redux";
import { makeStore, type AppStore } from "./index";

function createWrapper(store?: AppStore) {
	const s = store ?? makeStore();
	return function Wrapper({ children }: { children: React.ReactNode }) {
		return <Provider store={s}>{children}</Provider>;
	};
}

export function renderWithProviders(
	ui: React.ReactElement,
	{ store, ...renderOptions }: { store?: AppStore } & Omit<RenderOptions, "wrapper"> = {}
) {
	const s = store ?? makeStore();
	return { store: s, ...render(ui, { wrapper: createWrapper(s), ...renderOptions }) };
}

export function renderHookWithProviders<T>(hook: () => T, { store }: { store?: AppStore } = {}) {
	return renderHook(hook, { wrapper: createWrapper(store) });
}